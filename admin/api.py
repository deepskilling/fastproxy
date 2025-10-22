"""
Admin API - Configuration management and status endpoints
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reload")
async def reload_config(request: Request):
    """
    Hot reload configuration from config.yaml
    
    Reloads routing configuration without restarting the server.
    Validates configuration before applying.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Reload configuration
        router_instance = request.app.state.router
        config = router_instance.load_config()
        
        # Update rate limiter if config changed
        rate_limit_config = router_instance.get_rate_limit_config()
        requests_per_minute = rate_limit_config.get('requests_per_minute', 100)
        request.app.state.rate_limiter.update_limit(requests_per_minute)
        
        # Log admin action
        if hasattr(request.app.state, 'audit_logger'):
            request.app.state.audit_logger.log_admin_action(
                client_ip=client_ip,
                action="config_reload",
                details=f"Reloaded {len(router_instance.routes)} routes"
            )
        
        logger.info(f"Configuration reloaded successfully by {client_ip}")
        
        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "routes_count": len(router_instance.routes),
            "rate_limit": requests_per_minute
        }
        
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        
        # Log failed admin action
        if hasattr(request.app.state, 'audit_logger'):
            request.app.state.audit_logger.log_admin_action(
                client_ip=client_ip,
                action="config_reload_failed",
                details=str(e)
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@router.get("/routes")
async def list_routes(request: Request) -> List[Dict[str, str]]:
    """
    List all configured routes
    
    Returns the current routing configuration.
    """
    router_instance = request.app.state.router
    routes = router_instance.get_routes()
    
    return routes


@router.get("/config")
async def get_config(request: Request) -> Dict:
    """
    Get full current configuration
    
    Returns the complete configuration including routes, rate limits, and CORS settings.
    """
    router_instance = request.app.state.router
    config = router_instance.get_config()
    
    return {
        "status": "success",
        "config": config
    }


@router.get("/status")
async def get_status(request: Request):
    """
    Get proxy server status and statistics
    
    Returns current server status including route count, rate limiter state, and audit stats.
    """
    router_instance = request.app.state.router
    rate_limiter = request.app.state.rate_limiter
    
    # Get audit stats if available
    audit_stats = {}
    if hasattr(request.app.state, 'audit_logger'):
        audit_stats = request.app.state.audit_logger.get_stats()
    
    return {
        "status": "running",
        "routes_count": len(router_instance.routes),
        "rate_limit": {
            "requests_per_minute": rate_limiter.requests_per_minute,
            "window_size": rate_limiter.window_size
        },
        "audit": audit_stats
    }


@router.post("/ratelimit/clear/{ip}")
async def clear_rate_limit(request: Request, ip: str):
    """
    Clear rate limit for a specific IP address
    
    Removes all rate limit history for the specified IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter = request.app.state.rate_limiter
    
    rate_limiter.clear_ip(ip)
    
    # Log admin action
    if hasattr(request.app.state, 'audit_logger'):
        request.app.state.audit_logger.log_admin_action(
            client_ip=client_ip,
            action="rate_limit_clear",
            details=f"Cleared rate limit for {ip}"
        )
    
    return {
        "status": "success",
        "message": f"Rate limit cleared for {ip}"
    }


@router.get("/ratelimit/stats/{ip}")
async def get_rate_limit_stats(request: Request, ip: str):
    """
    Get rate limit statistics for a specific IP
    
    Returns current rate limit usage for the specified IP.
    """
    rate_limiter = request.app.state.rate_limiter
    stats = rate_limiter.get_stats(ip)
    
    return stats

