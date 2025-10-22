"""
Middleware - Request logging and custom headers
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all incoming requests and responses
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Log request details and response time
        """
        # Skip logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # ms
            
            # Log response
            logger.info(
                f"← {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration:.2f}ms)"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = f"{duration:.2f}ms"
            response.headers["X-Proxy-By"] = "FastProxy"
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"✗ {request.method} {request.url.path} "
                f"→ ERROR ({duration:.2f}ms): {e}"
            )
            raise

