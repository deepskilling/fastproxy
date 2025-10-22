"""
Audit Logger - SQLite-based audit log storage
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from audit.models import AuditEntry, AUDIT_SCHEMA

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    SQLite-based audit logger for requests and admin actions
    """
    
    def __init__(self, db_path: str = "audit/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            self.conn.executescript(AUDIT_SCHEMA)
            self.conn.commit()
            logger.info(f"Audit database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize audit database: {e}")
            raise
    
    def log_request(
        self,
        client_ip: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_agent: Optional[str] = None
    ):
        """Log an HTTP request"""
        try:
            self.conn.execute(
                """
                INSERT INTO audit_log 
                (timestamp, event_type, client_ip, method, path, status_code, duration_ms, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    "request",
                    client_ip,
                    method,
                    path,
                    status_code,
                    duration_ms,
                    user_agent
                )
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
    
    def log_admin_action(
        self,
        client_ip: str,
        action: str,
        details: Optional[str] = None
    ):
        """Log an admin action"""
        try:
            self.conn.execute(
                """
                INSERT INTO audit_log 
                (timestamp, event_type, client_ip, action, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    "admin_action",
                    client_ip,
                    action,
                    details
                )
            )
            self.conn.commit()
            logger.info(f"Admin action logged: {action} from {client_ip}")
        except Exception as e:
            logger.error(f"Failed to log admin action: {e}")
    
    def get_recent_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> List[AuditEntry]:
        """Fetch recent audit logs"""
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if client_ip:
                query += " AND client_ip = ?"
                params.append(client_ip)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = self.conn.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to AuditEntry objects
            entries = []
            for row in rows:
                entry = AuditEntry(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    event_type=row[2],
                    client_ip=row[3],
                    method=row[4],
                    path=row[5],
                    status_code=row[6],
                    duration_ms=row[7],
                    action=row[8],
                    details=row[9],
                    user_agent=row[10]
                )
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to fetch audit logs: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get audit log statistics"""
        try:
            cursor = self.conn.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN event_type = 'request' THEN 1 ELSE 0 END) as requests,
                    SUM(CASE WHEN event_type = 'admin_action' THEN 1 ELSE 0 END) as admin_actions
                FROM audit_log
                """
            )
            row = cursor.fetchone()
            
            return {
                "total_entries": row[0],
                "request_count": row[1],
                "admin_action_count": row[2]
            }
        except Exception as e:
            logger.error(f"Failed to get audit stats: {e}")
            return {"total_entries": 0, "request_count": 0, "admin_action_count": 0}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Audit database connection closed")

