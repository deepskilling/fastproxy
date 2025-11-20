"""
FastProxy Management API Backend
Provides REST API endpoints for managing the FastProxy service
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import os
import yaml
import json
from pathlib import Path

app = FastAPI(
    title="FastProxy Management API",
    description="API for managing FastProxy configuration and monitoring",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Frontend dev server (direct)
        "http://localhost:5173",      # Alternative dev port
        "http://localhost:8000",      # FastProxy reverse proxy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)  # auto_error=False makes auth optional for development

# Configuration paths
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"
API_KEYS_DB = Path(__file__).parent.parent.parent / "security" / "api_keys.db"

# Pydantic Models
class RouteConfig(BaseModel):
    """Proxy route configuration"""
    path: str = Field(..., description="Route path pattern")
    target: str = Field(..., description="Target backend URL")
    methods: Optional[List[str]] = Field(default=["GET", "POST", "PUT", "DELETE"], description="Allowed HTTP methods")
    auth_required: bool = Field(default=False, description="Whether authentication is required")
    rate_limit: Optional[int] = Field(default=None, description="Rate limit per minute")

class ProxyStats(BaseModel):
    """Proxy statistics"""
    total_requests: int
    active_routes: int
    uptime: str
    last_updated: datetime

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str

class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    config: Dict[str, Any]

class ApiKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., description="Name/description for the API key")
    permissions: List[str] = Field(default=["read"], description="List of permissions")
    expires_in_days: Optional[int] = Field(default=None, description="Number of days until expiration")

class ApiKeyResponse(BaseModel):
    """API key response"""
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime]

# Helper Functions
def load_config() -> dict:
    """Load FastProxy configuration"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load configuration: {str(e)}")

def save_config(config: dict) -> None:
    """Save FastProxy configuration"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify JWT token or API key"""
    # TODO: Implement proper token verification
    # For now, allow access without authentication for development
    if credentials:
        return credentials.credentials
    return None  # Allow unauthenticated access for development

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

@app.get("/api/config")
async def get_config(token: str = Depends(verify_token)):
    """Get current FastProxy configuration"""
    config = load_config()
    return {"config": config}

@app.put("/api/config")
async def update_config(
    request: ConfigUpdateRequest,
    token: str = Depends(verify_token)
):
    """Update FastProxy configuration"""
    try:
        save_config(request.config)
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/routes")
async def get_routes(token: str = Depends(verify_token)):
    """Get all configured proxy routes"""
    config = load_config()
    routes = config.get('routes', [])
    return {"routes": routes}

@app.post("/api/routes")
async def add_route(
    route: RouteConfig,
    token: str = Depends(verify_token)
):
    """Add a new proxy route"""
    config = load_config()
    if 'routes' not in config:
        config['routes'] = []
    
    # Check for duplicate path
    if any(r.get('path') == route.path for r in config['routes']):
        raise HTTPException(status_code=400, detail="Route path already exists")
    
    config['routes'].append(route.dict())
    save_config(config)
    
    return {
        "status": "success",
        "message": "Route added successfully",
        "route": route
    }

@app.delete("/api/routes/{path:path}")
async def delete_route(
    path: str,
    token: str = Depends(verify_token)
):
    """Delete a proxy route"""
    config = load_config()
    routes = config.get('routes', [])
    
    # Find and remove the route
    updated_routes = [r for r in routes if r.get('path') != f"/{path}"]
    
    if len(updated_routes) == len(routes):
        raise HTTPException(status_code=404, detail="Route not found")
    
    config['routes'] = updated_routes
    save_config(config)
    
    return {
        "status": "success",
        "message": "Route deleted successfully"
    }

@app.get("/api/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get proxy statistics"""
    config = load_config()
    routes = config.get('routes', [])
    
    # TODO: Implement actual statistics collection
    return {
        "total_requests": 0,
        "active_routes": len(routes),
        "uptime": "N/A",
        "last_updated": datetime.now()
    }

@app.post("/api/keys")
async def create_api_key(
    request: ApiKeyCreate,
    token: str = Depends(verify_token)
):
    """Create a new API key"""
    # TODO: Implement API key creation
    import secrets
    new_key = f"fp_{secrets.token_urlsafe(32)}"
    
    return {
        "key": new_key,
        "name": request.name,
        "created_at": datetime.now(),
        "expires_at": None
    }

@app.get("/api/keys")
async def list_api_keys(token: str = Depends(verify_token)):
    """List all API keys (without revealing the actual keys)"""
    # TODO: Implement API key listing from database
    return {"keys": []}

@app.delete("/api/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    token: str = Depends(verify_token)
):
    """Revoke an API key"""
    # TODO: Implement API key revocation
    return {
        "status": "success",
        "message": "API key revoked successfully"
    }

# Admin endpoints
@app.post("/api/proxy/restart")
async def restart_proxy(token: str = Depends(verify_token)):
    """Restart the FastProxy service"""
    # TODO: Implement proxy restart logic
    return {
        "status": "success",
        "message": "Proxy restart initiated"
    }

@app.get("/api/logs")
async def get_logs(
    limit: int = 100,
    level: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Get recent proxy logs"""
    # TODO: Implement log retrieval
    return {"logs": []}

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

