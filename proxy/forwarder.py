"""
Forwarder - Async HTTP request forwarding using httpx
"""
import httpx
import logging
from fastapi import Request
from fastapi.responses import Response

logger = logging.getLogger(__name__)

# Global async client (reused across requests)
client = httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=True,
    limits=httpx.Limits(max_keepalive_connections=100, max_connections=200)
)


async def forward_request(request: Request, target_url: str, path: str) -> Response:
    """
    Forward incoming request to target backend server
    
    Args:
        request: Incoming FastAPI request
        target_url: Target backend URL (e.g., http://127.0.0.1:8001)
        path: Request path
    
    Returns:
        Response from backend server
    """
    # Build full target URL
    target_path = path
    if not target_path.startswith('/'):
        target_path = f"/{target_path}"
    
    full_url = f"{target_url.rstrip('/')}{target_path}"
    if request.url.query:
        full_url = f"{full_url}?{request.url.query}"
    
    # Prepare headers (exclude host and other hop-by-hop headers)
    headers = dict(request.headers)
    excluded_headers = ['host', 'connection', 'keep-alive', 'proxy-authenticate', 
                       'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']
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
        response_headers = dict(response.headers)
        for header in excluded_headers:
            response_headers.pop(header, None)
        
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
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

