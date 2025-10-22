"""
Audit Middleware - Intercepts requests for audit logging
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to audit log all requests
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Log all requests to audit database
        """
        # Skip audit logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # ms
            
            # Log to audit database
            if hasattr(request.app.state, 'audit_logger'):
                request.app.state.audit_logger.log_request(
                    client_ip=client_ip,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration,
                    user_agent=user_agent
                )
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            # Log error to audit
            if hasattr(request.app.state, 'audit_logger'):
                request.app.state.audit_logger.log_request(
                    client_ip=client_ip,
                    method=request.method,
                    path=request.url.path,
                    status_code=500,
                    duration_ms=duration,
                    user_agent=user_agent
                )
            
            raise

