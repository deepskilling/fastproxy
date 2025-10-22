"""
Security Middleware - Headers, body size limits, etc.
"""
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Maximum request body size (10 MB default)
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


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
    Enforce request body size limits to prevent DoS
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Check request body size before processing"""
        
        # Get Content-Length header
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            
            if content_length > MAX_BODY_SIZE:
                logger.warning(
                    f"Request body too large: {content_length} bytes "
                    f"(max: {MAX_BODY_SIZE}) from {request.client.host}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {MAX_BODY_SIZE} bytes"
                )
        
        return await call_next(request)

