"""
Authentication and Authorization for Admin/Audit Endpoints
"""
import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# Load admin credentials from environment variables
# CRITICAL: Set these environment variables before running!
ADMIN_USERNAME = os.getenv("FASTPROXY_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("FASTPROXY_ADMIN_PASSWORD", "change_this_password")

# CRITICAL WARNING: Change default credentials immediately!
if ADMIN_PASSWORD == "change_this_password":
    import logging
    logging.warning(
        "⚠️  SECURITY WARNING: Using default admin password! "
        "Set FASTPROXY_ADMIN_PASSWORD environment variable immediately!"
    )


def verify_admin_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Verify admin credentials using constant-time comparison
    
    Args:
        credentials: HTTP Basic Auth credentials
    
    Returns:
        True if credentials are valid, False otherwise
    """
    # Use constant-time comparison to prevent timing attacks
    username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"),
        ADMIN_USERNAME.encode("utf8")
    )
    password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"),
        ADMIN_PASSWORD.encode("utf8")
    )
    
    return username_correct and password_correct


def require_admin(credentials: HTTPBasicCredentials = Security(security)) -> str:
    """
    Dependency to require admin authentication
    
    Usage:
        @router.get("/protected")
        async def protected_route(username: str = Depends(require_admin)):
            return {"message": f"Hello {username}"}
    
    Raises:
        HTTPException: 401 if credentials are invalid
    
    Returns:
        Username if authenticated
    """
    if not verify_admin_credentials(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

