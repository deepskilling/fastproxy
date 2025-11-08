"""
Authentication and Authorization for Admin/Audit Endpoints
"""
import os
import secrets
import logging
from typing import Optional, Annotated
from fastapi import HTTPException, Security, status, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

security = HTTPBasic()

# Load admin credentials from environment variables
# CRITICAL: Set these environment variables before running!
ADMIN_USERNAME = os.getenv("FASTPROXY_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("FASTPROXY_ADMIN_PASSWORD", "change_this_password")

# CRITICAL WARNING: Change default credentials immediately!
if ADMIN_PASSWORD == "change_this_password":
    logger.warning(
        "⚠️  SECURITY WARNING: Using default admin password! "
        "Set FASTPROXY_ADMIN_PASSWORD environment variable immediately!"
    )

# Track failed authentication attempts for brute force detection
# Structure: {ip: [(timestamp1, username1), (timestamp2, username2), ...]}
failed_auth_attempts: dict = defaultdict(list)
FAILED_AUTH_WINDOW = 300  # 5 minutes
MAX_FAILED_ATTEMPTS = 5


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


def check_brute_force(client_ip: str) -> bool:
    """
    Check if IP has exceeded failed authentication attempts
    
    Args:
        client_ip: Client IP address
    
    Returns:
        True if IP is allowed to attempt authentication, False if blocked
    """
    current_time = time.time()
    cutoff_time = current_time - FAILED_AUTH_WINDOW
    
    # Clean old attempts
    attempts = failed_auth_attempts[client_ip]
    attempts[:] = [(t, u) for t, u in attempts if t > cutoff_time]
    
    # Check if exceeded limit
    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        return False
    
    return True


def record_failed_auth(client_ip: str, username: str):
    """
    Record a failed authentication attempt
    
    Args:
        client_ip: Client IP address
        username: Attempted username
    """
    current_time = time.time()
    failed_auth_attempts[client_ip].append((current_time, username))
    
    # Log warning if approaching limit
    attempt_count = len(failed_auth_attempts[client_ip])
    if attempt_count >= MAX_FAILED_ATTEMPTS:
        logger.error(
            f"🚨 BRUTE FORCE DETECTED: {client_ip} has {attempt_count} failed "
            f"authentication attempts in the last {FAILED_AUTH_WINDOW // 60} minutes"
        )
    elif attempt_count >= 3:
        logger.warning(
            f"⚠️  Multiple failed auth attempts from {client_ip}: "
            f"{attempt_count}/{MAX_FAILED_ATTEMPTS}"
        )


def require_admin(
    request: Request,
    credentials: HTTPBasicCredentials = Security(security)
) -> str:
    """
    Dependency to require admin authentication with logging and brute force protection
    
    Usage:
        @router.get("/protected")
        async def protected_route(
            request: Request,
            username: str = Depends(require_admin)
        ):
            return {"message": f"Hello {username}"}
    
    Raises:
        HTTPException: 401 if credentials are invalid or too many failed attempts
    
    Returns:
        Username if authenticated
    """
    # Get client IP from request
    client_ip = "unknown"
    if request and request.client:
        client_ip = request.client.host
    
    # Check for brute force attempts
    if not check_brute_force(client_ip):
        logger.error(
            f"🚨 BLOCKED: {client_ip} exceeded maximum failed authentication attempts "
            f"({MAX_FAILED_ATTEMPTS} in {FAILED_AUTH_WINDOW // 60} minutes)"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed authentication attempts. Please try again later.",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Verify credentials
    if not verify_admin_credentials(credentials):
        # Log failed authentication attempt
        logger.warning(
            f"❌ Failed admin authentication attempt - username: '{credentials.username}', "
            f"from IP: {client_ip}"
        )
        
        # Record failed attempt for brute force tracking
        record_failed_auth(client_ip, credentials.username)
        
        # Log to audit database if available
        if request and hasattr(request.app.state, 'audit_logger'):
            try:
                request.app.state.audit_logger.log_admin_action(
                    client_ip=client_ip,
                    action="auth_failed",
                    details=f"Failed login attempt for user: {credentials.username}"
                )
            except Exception as e:
                logger.error(f"Failed to log auth failure to audit database: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Successful authentication - clear failed attempts
    if client_ip in failed_auth_attempts:
        del failed_auth_attempts[client_ip]
    
    # Log successful authentication
    logger.info(f"✅ Successful admin authentication - username: '{credentials.username}', from IP: {client_ip}")
    
    return credentials.username

