"""
Forwarder - Async HTTP request forwarding using httpx with streaming support
"""
import httpx
import logging
from fastapi import Request
from fastapi.responses import StreamingResponse, Response
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Global async client (will be initialized with config)
client: Optional[httpx.AsyncClient] = None


def initialize_client(config: Dict):
    """
    Initialize the global HTTP client with configuration
    
    Args:
        config: Configuration dictionary from config.yaml
    """
    global client
    
    # Get proxy settings from config
    proxy_config = config.get('proxy_settings', {})
    timeout = proxy_config.get('timeout', 30.0)
    max_keepalive = proxy_config.get('max_keepalive_connections', 100)
    max_connections = proxy_config.get('max_connections', 200)
    
    client = httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        limits=httpx.Limits(
            max_keepalive_connections=max_keepalive,
            max_connections=max_connections
        )
    )
    
    logger.info(
        f"HTTP client initialized: timeout={timeout}s, "
        f"max_keepalive={max_keepalive}, max_connections={max_connections}"
    )


async def forward_request(request: Request, route: Dict, path: str) -> Response:
    """
    Forward incoming request to target backend server with streaming support
    
    Args:
        request: Incoming FastAPI request
        route: Route configuration dict with 'target', 'path', and optional 'strip_path'
        path: Request path
    
    Returns:
        Response from backend server
    """
    global client
    
    # Initialize client if not already done (fallback for safety)
    if client is None:
        logger.warning("Client not initialized, using default settings")
        client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
        )
    
    target_url = route['target']
    route_path = route['path']
    strip_path = route.get('strip_path', False)
    
    # Build target path
    target_path = f"/{path}"
    
    # Strip route prefix if configured
    if strip_path and target_path.startswith(route_path):
        target_path = target_path[len(route_path):]
        if not target_path:
            target_path = "/"
        elif not target_path.startswith('/'):
            target_path = f"/{target_path}"
        logger.debug(f"Stripped path: {route_path} -> {target_path}")
    
    # Build full target URL
    full_url = f"{target_url.rstrip('/')}{target_path}"
    if request.url.query:
        full_url = f"{full_url}?{request.url.query}"
    
    # Prepare headers (exclude host and other hop-by-hop headers)
    headers = dict(request.headers)
    excluded_headers = ['host', 'connection', 'keep-alive', 'proxy-authenticate', 
                       'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 
                       'upgrade', 'content-encoding']
    for header in excluded_headers:
        headers.pop(header, None)
    
    # Add X-Forwarded headers
    client_host = request.client.host if request.client else "unknown"
    headers['X-Forwarded-For'] = client_host
    headers['X-Forwarded-Proto'] = request.url.scheme
    headers['X-Forwarded-Host'] = request.url.netloc
    
    # Read request body
    body = await request.body()
    
    try:
        # Forward request
        logger.debug(f"Forwarding {request.method} {full_url}")
        
        response = await client.request(
            method=request.method,
            url=full_url,
            headers=headers,
            content=body,
        )
        
        # Prepare response headers (exclude hop-by-hop headers)
        response_headers = {}
        for key, value in response.headers.items():
            if key.lower() not in excluded_headers:
                response_headers[key] = value
        
        # Read the entire response content (httpx auto-decompresses)
        content = await response.aread()
        
        # Return response with decompressed content
        # DON'T include content-encoding header since we decompressed it
        return Response(
            content=content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get('content-type')
        )
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout forwarding to {full_url}: {e}")
        raise
    except httpx.ConnectError as e:
        logger.error(f"Connection error to {full_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error forwarding request to {full_url}: {e}")
        raise


async def close_client():
    """Close the global HTTP client"""
    global client
    if client:
        await client.aclose()
        logger.info("HTTP client closed")
