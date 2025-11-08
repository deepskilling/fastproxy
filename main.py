"""
FastProxy - FastAPI-based Reverse Proxy MVP
Main application entrypoint with async proxy forwarding and middleware
NOW WITH AUTOMATIC HTTPS!
"""
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from proxy.router import Router
from proxy.forwarder import forward_request, initialize_client, close_client
from proxy.rate_limit import RateLimiter
from proxy.middleware import RequestLoggingMiddleware
from audit.middleware import AuditMiddleware
from audit.logger import AuditLogger
from audit.api import router as audit_router
from admin.api import router as admin_router
from auth.api import router as auth_router
from security.middleware import SecurityHeadersMiddleware, RequestBodySizeLimitMiddleware

# Import certificate manager
from cert_manager.manager import CertificateManager

# Configure logging (will be updated from config later)
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
    
    # Load initial config
    try:
        config = app.state.router.load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize HTTP client with proxy settings
        initialize_client(config)
        
        # Initialize RateLimiter with config settings
        rate_limit_config = app.state.router.get_rate_limit_config()
        requests_per_minute = rate_limit_config.get('requests_per_minute', 100)
        app.state.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        logger.info(f"Rate limiter configured: {requests_per_minute} requests/minute")
        
        # Configure logging level if specified
        log_level = config.get('logging', {}).get('level', 'INFO')
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)
        logger.info(f"Logging level set to: {log_level}")
        
        # Store config for middleware access
        app.state.config = config
        
        # Initialize audit logger
        app.state.audit_logger = AuditLogger()
        
        # Initialize certificate manager for automatic HTTPS
        auto_https_config = config.get('auto_https', {})
        if auto_https_config.get('enabled', False):
            logger.info("🔒 Automatic HTTPS is ENABLED")
            
            domain = auto_https_config.get('domain')
            email = auto_https_config.get('email')
            staging = auto_https_config.get('staging', True)
            
            if not domain or not email:
                logger.error("❌ auto_https enabled but domain/email not configured!")
            else:
                app.state.cert_manager = CertificateManager(
                    domain=domain,
                    email=email,
                    staging=staging
                )
                
                # Check if certificate exists or request new one
                if not app.state.cert_manager.certificate_exists():
                    logger.info("📜 No existing certificate found, will request from Let's Encrypt")
                    logger.info(f"⚠️  Make sure port 80 is open and {domain} points to this server!")
                else:
                    logger.info("✅ Existing certificate found")
                
                # Start auto-renewal task if enabled
                if auto_https_config.get('auto_renew', True):
                    check_interval = auto_https_config.get('check_interval_hours', 24)
                    asyncio.create_task(
                        app.state.cert_manager.auto_renewal_task(check_interval)
                    )
                    logger.info(f"🔄 Auto-renewal task started (checking every {check_interval} hours)")
        else:
            logger.info("ℹ️  Automatic HTTPS is DISABLED (running in HTTP mode)")
            app.state.cert_manager = None
        
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastProxy server...")
    app.state.audit_logger.close()
    await close_client()


# Create FastAPI app
app = FastAPI(
    title="FastProxy",
    description="FastAPI-based Reverse Proxy with Automatic HTTPS",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware will be added dynamically after config is loaded
# This is a workaround since middleware must be added before startup
# We'll read from config in a startup event
@app.on_event("startup")
async def configure_cors():
    """Configure CORS from config.yaml"""
    cors_config = app.state.router.get_cors_config()
    
    # Note: CORS middleware was already added in the middleware stack below
    # This logs the configuration being used
    logger.info(f"✅ CORS configured from config.yaml: {cors_config}")


# Add CORS middleware with config.yaml settings
# We need to create a temporary router to read config before app starts
_temp_router = Router()
_temp_config = _temp_router.load_config()
_cors_config = _temp_router.get_cors_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_config.get('allow_origins', ['*']),
    allow_credentials=_cors_config.get('allow_credentials', True),
    allow_methods=_cors_config.get('allow_methods', ['*']),
    allow_headers=_cors_config.get('allow_headers', ['*']),
)
logger.info(f"✅ CORS middleware configured from config.yaml")

# Add security middlewares (ORDER MATTERS!)
# app.add_middleware(SecurityHeadersMiddleware)  # Disabled - breaks frontend
app.add_middleware(RequestBodySizeLimitMiddleware) # Enforce body size limit (reads from config)
app.add_middleware(RequestLoggingMiddleware)        # Log requests
app.add_middleware(AuditMiddleware)                 # Audit logging

# Include routers
app.include_router(auth_router, tags=["authentication"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cert_status = "disabled"
    if hasattr(app.state, 'cert_manager') and app.state.cert_manager:
        if app.state.cert_manager.certificate_exists():
            expiry = app.state.cert_manager.get_certificate_expiry()
            if expiry:
                days_left = (expiry - datetime.now()).days
                cert_status = f"valid ({days_left} days left)"
        else:
            cert_status = "no certificate"
    
    return {
        "status": "healthy",
        "service": "fastproxy",
        "version": "2.0.0",
        "features": {
            "automatic_https": cert_status,
            "rate_limiting": "enabled",
            "audit_logging": "enabled"
        }
    }


# ACME HTTP-01 Challenge Handler
@app.get("/.well-known/acme-challenge/{token}")
async def acme_challenge(token: str):
    """
    Handle Let's Encrypt HTTP-01 challenge
    This endpoint serves challenge responses for certificate verification
    """
    if not hasattr(app.state, 'cert_manager') or not app.state.cert_manager:
        logger.warning(f"ACME challenge requested but cert_manager not initialized")
        return JSONResponse(
            status_code=404,
            content={"error": "Automatic HTTPS not enabled"}
        )
    
    response = app.state.cert_manager.get_challenge_response(token)
    if response:
        logger.info(f"✅ Serving ACME challenge response for token: {token}")
        return PlainTextResponse(content=response)
    else:
        logger.warning(f"❌ No challenge response found for token: {token}")
        return JSONResponse(
            status_code=404,
            content={"error": "Challenge not found"}
        )


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
    
    # Forward request with route configuration (for path stripping support)
    try:
        response = await forward_request(request, route, path)
        return response
    except Exception as e:
        # Log detailed error internally (with stack trace)
        logger.error(f"Error forwarding request to {route['target']}: {e}", exc_info=True)
        
        # Return generic error to client (no details leaked)
        return JSONResponse(
            status_code=502,
            content={"error": "Bad Gateway"}
        )


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    # Load config to check auto_https settings
    router = Router()
    config = router.load_config()
    auto_https_config = config.get('auto_https', {})
    
    if auto_https_config.get('enabled', False):
        # Run with HTTPS (automatic Let's Encrypt)
        domain = auto_https_config.get('domain')
        logger.info(f"🔒 Starting FastProxy with Automatic HTTPS for {domain}")
        logger.info(f"⚠️  Make sure DNS points to this server and port 80/443 are open!")
        
        # Initialize cert manager to get SSL context
        cert_manager = CertificateManager(
            domain=domain,
            email=auto_https_config.get('email'),
            staging=auto_https_config.get('staging', True)
        )
        
        # Request certificate if doesn't exist
        if not cert_manager.certificate_exists():
            logger.info("📜 Requesting certificate from Let's Encrypt...")
            logger.info("ℹ️  This requires port 80 to be accessible for HTTP-01 challenge")
            # Note: Certificate will be requested when the server receives the challenge
        
        ssl_context = cert_manager.get_ssl_context()
        if ssl_context:
            uvicorn.run(
                "main:app",
                host="0.0.0.0",
                port=443,
                ssl_context=ssl_context,
                reload=False,
                log_level="info"
            )
        else:
            logger.error("❌ Failed to get SSL context, falling back to HTTP")
            uvicorn.run(
                "main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="info"
            )
    else:
        # Run with HTTP (development/testing mode)
        logger.warning("⚠️  Running in HTTP mode (automatic HTTPS disabled)")
        logger.info("ℹ️  Enable auto_https in config.yaml for production")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
