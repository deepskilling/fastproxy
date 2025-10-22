"""
FastProxy - FastAPI-based Reverse Proxy MVP
Main application entrypoint with async proxy forwarding and middleware
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from proxy.router import Router
from proxy.forwarder import forward_request
from proxy.rate_limit import RateLimiter
from proxy.middleware import RequestLoggingMiddleware
from audit.middleware import AuditMiddleware
from audit.logger import AuditLogger
from audit.api import router as audit_router
from admin.api import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting FastProxy server...")
    app.state.router = Router()
    app.state.rate_limiter = RateLimiter()
    app.state.audit_logger = AuditLogger()
    
    # Load initial config
    try:
        app.state.router.load_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastProxy server...")
    app.state.audit_logger.close()


# Create FastAPI app
app = FastAPI(
    title="FastProxy",
    description="FastAPI-based Reverse Proxy (Nginx-lite)",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuditMiddleware)

# Include routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fastproxy"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_handler(request: Request, path: str):
    """
    Main proxy handler - forwards requests to configured backends
    """
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not app.state.rate_limiter.allow_request(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    # Find matching route
    route = app.state.router.match_route(f"/{path}")
    if not route:
        logger.warning(f"No route found for path: /{path}")
        return JSONResponse(
            status_code=404,
            content={"error": "No matching route found"}
        )
    
    # Forward request
    try:
        response = await forward_request(request, route["target"], path)
        return response
    except Exception as e:
        logger.error(f"Error forwarding request: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway", "detail": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

