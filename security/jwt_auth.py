"""
JWT Token Authentication
More secure alternative to HTTP Basic Auth
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("FASTPROXY_JWT_SECRET", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security warning for default secret
if SECRET_KEY == "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION":
    logger.warning(
        "⚠️  SECURITY WARNING: Using default JWT secret key! "
        "Set FASTPROXY_JWT_SECRET environment variable immediately!"
    )

# Bearer token security
bearer_scheme = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data"""
    username: str
    exp: datetime
    token_type: str = "access"


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def create_token(username: str, token_type: str = "access", 
                 expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT token
    
    Args:
        username: Username to encode in token
        token_type: 'access' or 'refresh'
        expires_delta: Custom expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        if token_type == "access":
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:  # refresh token
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": username,
        "exp": expire,
        "type": token_type,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(username: str) -> str:
    """Create access token (short-lived)"""
    return create_token(username, token_type="access")


def create_refresh_token(username: str) -> str:
    """Create refresh token (long-lived)"""
    return create_token(username, token_type="refresh")


def create_token_pair(username: str) -> TokenResponse:
    """
    Create both access and refresh tokens
    
    Args:
        username: Username to create tokens for
    
    Returns:
        TokenResponse with both tokens
    """
    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def verify_token(token: str, token_type: str = "access") -> str:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ('access' or 'refresh')
    
    Returns:
        Username from token
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type_from_payload: str = payload.get("type")
        
        if username is None:
            logger.warning("Token missing username")
            raise credentials_exception
        
        if token_type_from_payload != token_type:
            logger.warning(
                f"Invalid token type. Expected {token_type}, "
                f"got {token_type_from_payload}"
            )
            raise credentials_exception
        
        return username
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise credentials_exception


def require_jwt_auth(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> str:
    """
    Dependency to require JWT authentication
    
    Usage:
        @router.get("/protected")
        async def protected_route(username: str = Depends(require_jwt_auth)):
            return {"message": f"Hello {username}"}
    
    Args:
        credentials: Bearer token from Authorization header
    
    Returns:
        Username if token is valid
    
    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials
    username = verify_token(token, token_type="access")
    
    logger.info(f"JWT auth successful for user: {username}")
    return username


def require_refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> str:
    """
    Dependency to require refresh token (for token refresh endpoint)
    
    Args:
        credentials: Bearer token from Authorization header
    
    Returns:
        Username if refresh token is valid
    
    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials
    username = verify_token(token, token_type="refresh")
    
    logger.info(f"Refresh token validated for user: {username}")
    return username

