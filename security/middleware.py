"""
Security Middleware - Headers, body size limits, etc.
"""
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response"""
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS - Force HTTPS (only if using HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy (restrictive)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Don't leak referrer to external sites
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (disable unnecessary features)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestBodySizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Enforce maximum request body size
    Reads max_body_size from config.yaml (default: 10 MB)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Check and enforce body size limit"""
        
        # Get max_body_size from app config (set during startup)
        max_body_size = 10 * 1024 * 1024  # Default: 10 MB
        
        if hasattr(request.app.state, 'config'):
            max_body_size = request.app.state.config.get('max_body_size', max_body_size)
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > max_body_size:
                logger.warning(
                    f"Request body too large: {content_length} bytes "
                    f"(max: {max_body_size} bytes) from {request.client.host if request.client else 'unknown'}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {max_body_size} bytes"
                )
        
        return await call_next(request)
