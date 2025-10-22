"""
API Key Authentication
For service-to-service authentication and automation
"""
import os
import secrets
import hashlib
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKey(BaseModel):
    """API Key model"""
    key_id: str
    name: str
    key_prefix: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True


class APIKeyCreate(BaseModel):
    """API Key creation request"""
    name: str
    description: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API Key creation response (includes the actual key)"""
    key_id: str
    name: str
    api_key: str  # Only shown once!
    key_prefix: str
    created_at: datetime
    warning: str = "⚠️  Save this API key securely. It will not be shown again!"


class APIKeyManager:
    """
    Manages API keys with SQLite storage
    Keys are hashed using SHA-256
    """
    
    def __init__(self, db_path: str = "security/api_keys.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize API keys database"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                key_prefix TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                last_used TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_key_hash ON api_keys(key_hash)
        """)
        conn.commit()
        conn.close()
        logger.info(f"API keys database initialized at {self.db_path}")
    
    def _hash_key(self, api_key: str) -> str:
        """Hash API key using SHA-256"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def generate_key(self, name: str, description: Optional[str] = None) -> APIKeyResponse:
        """
        Generate a new API key
        
        Args:
            name: Friendly name for the key
            description: Optional description
        
        Returns:
            APIKeyResponse with the actual key (only shown once!)
        """
        # Generate secure random key
        api_key = f"fpx_{secrets.token_urlsafe(32)}"
        key_id = secrets.token_hex(8)
        key_hash = self._hash_key(api_key)
        key_prefix = api_key[:11]  # "fpx_" + first 7 chars
        created_at = datetime.utcnow().isoformat()
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                INSERT INTO api_keys (key_id, name, key_hash, key_prefix, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (key_id, name, key_hash, key_prefix, description, created_at))
            conn.commit()
            
            logger.info(f"Generated API key: {key_id} for {name}")
            
            return APIKeyResponse(
                key_id=key_id,
                name=name,
                api_key=api_key,
                key_prefix=key_prefix,
                created_at=datetime.fromisoformat(created_at)
            )
        finally:
            conn.close()
    
    def verify_key(self, api_key: str) -> Optional[str]:
        """
        Verify API key and return key_id if valid
        
        Args:
            api_key: API key to verify
        
        Returns:
            key_id if valid, None otherwise
        """
        if not api_key or not api_key.startswith("fpx_"):
            return None
        
        key_hash = self._hash_key(api_key)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("""
                SELECT key_id, is_active FROM api_keys
                WHERE key_hash = ?
            """, (key_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            key_id, is_active = row
            
            if not is_active:
                logger.warning(f"Attempted use of disabled API key: {key_id}")
                return None
            
            # Update last_used timestamp
            conn.execute("""
                UPDATE api_keys SET last_used = ?
                WHERE key_id = ?
            """, (datetime.utcnow().isoformat(), key_id))
            conn.commit()
            
            logger.info(f"API key verified: {key_id}")
            return key_id
            
        finally:
            conn.close()
    
    def list_keys(self) -> List[APIKey]:
        """List all API keys (without actual keys)"""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("""
                SELECT key_id, name, key_prefix, created_at, last_used, is_active
                FROM api_keys
                ORDER BY created_at DESC
            """)
            
            keys = []
            for row in cursor.fetchall():
                keys.append(APIKey(
                    key_id=row[0],
                    name=row[1],
                    key_prefix=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    last_used=datetime.fromisoformat(row[4]) if row[4] else None,
                    is_active=bool(row[5])
                ))
            
            return keys
        finally:
            conn.close()
    
    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke (disable) an API key
        
        Args:
            key_id: ID of key to revoke
        
        Returns:
            True if revoked, False if not found
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("""
                UPDATE api_keys SET is_active = 0
                WHERE key_id = ?
            """, (key_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Revoked API key: {key_id}")
                return True
            return False
        finally:
            conn.close()
    
    def delete_key(self, key_id: str) -> bool:
        """
        Permanently delete an API key
        
        Args:
            key_id: ID of key to delete
        
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("""
                DELETE FROM api_keys WHERE key_id = ?
            """, (key_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Deleted API key: {key_id}")
                return True
            return False
        finally:
            conn.close()


# Global API key manager instance
api_key_manager = APIKeyManager()


def require_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Dependency to require API key authentication
    
    Usage:
        @router.get("/protected")
        async def protected_route(key_id: str = Depends(require_api_key)):
            return {"message": f"Authenticated with key {key_id}"}
    
    Args:
        api_key: API key from X-API-Key header
    
    Returns:
        key_id if API key is valid
    
    Raises:
        HTTPException: 401 if API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    key_id = api_key_manager.verify_key(api_key)
    
    if not key_id:
        logger.warning(f"Invalid API key attempted from header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return key_id

