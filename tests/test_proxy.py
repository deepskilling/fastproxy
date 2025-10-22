"""
Tests for proxy routing and forwarding
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import httpx

from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "fastproxy"


def test_route_matching():
    """Test route matching logic"""
    from proxy.router import Router
    
    router = Router()
    router.routes = [
        {"path": "/api/", "target": "http://backend1:8001"},
        {"path": "/auth/", "target": "http://backend2:8002"},
        {"path": "/", "target": "http://default:8000"}
    ]
    
    # Test exact prefix match
    route = router.match_route("/api/users")
    assert route is not None
    assert route["target"] == "http://backend1:8001"
    
    # Test longer path match
    route = router.match_route("/auth/login")
    assert route is not None
    assert route["target"] == "http://backend2:8002"
    
    # Test default route
    route = router.match_route("/other")
    assert route is not None
    assert route["target"] == "http://default:8000"
    
    # Test no match (when no default)
    router.routes = [
        {"path": "/api/", "target": "http://backend1:8001"}
    ]
    route = router.match_route("/other")
    assert route is None


def test_config_validation():
    """Test configuration validation"""
    from proxy.router import Router
    
    router = Router()
    
    # Test missing path
    router.routes = [{"target": "http://backend:8001"}]
    with pytest.raises(ValueError, match="missing 'path' or 'target'"):
        router._validate_routes()
    
    # Test invalid path (not starting with /)
    router.routes = [{"path": "api/", "target": "http://backend:8001"}]
    with pytest.raises(ValueError, match="must start with '/'"):
        router._validate_routes()
    
    # Test invalid target URL
    router.routes = [{"path": "/api/", "target": "backend:8001"}]
    with pytest.raises(ValueError, match="must be valid HTTP URL"):
        router._validate_routes()


@pytest.mark.asyncio
async def test_request_forwarding():
    """Test async request forwarding"""
    from proxy.forwarder import forward_request
    from fastapi import Request
    
    # Mock request
    mock_request = Mock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.query = ""
    mock_request.url.scheme = "http"
    mock_request.url.netloc = "localhost:8000"
    mock_request.headers = {"user-agent": "test"}
    mock_request.client.host = "127.0.0.1"
    mock_request.body = AsyncMock(return_value=b"")
    
    # Mock httpx response
    mock_response = Mock()
    mock_response.content = b'{"result": "success"}'
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    
    # Patch httpx client
    with patch('proxy.forwarder.client.request', new_callable=AsyncMock) as mock_client:
        mock_client.return_value = mock_response
        
        response = await forward_request(
            mock_request,
            "http://backend:8001",
            "/api/test"
        )
        
        assert response.status_code == 200
        assert response.body == b'{"result": "success"}'
        
        # Verify request was made with correct parameters
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args.kwargs
        assert call_kwargs["method"] == "GET"
        assert "http://backend:8001/api/test" in call_kwargs["url"]


def test_no_route_found(client):
    """Test behavior when no route matches"""
    # Assuming default config doesn't have a catch-all route
    response = client.get("/nonexistent/path")
    assert response.status_code == 404
    assert "No matching route found" in response.json()["error"]

