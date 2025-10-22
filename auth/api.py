"""
Authentication API Endpoints
Handles JWT login, token refresh, and API key management
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from security.jwt_auth import (
    create_token_pair, TokenResponse, require_refresh_token,
    create_access_token
)
from security.api_keys import (
    api_key_manager, APIKey, APIKeyCreate, APIKeyResponse,
    require_api_key
)
from security.auth import verify_admin_credentials
from security.rate_limiter_admin import admin_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBasic()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security)
):
    """
    Login with username/password to get JWT tokens
    
    Returns:
        - access_token: Short-lived token (30 minutes)
        - refresh_token: Long-lived token (7 days)
    
    Rate Limited: 5 attempts per 5 minutes per IP
    """
    # Apply rate limiting
    admin_rate_limiter.check_rate_limit(request, endpoint="login")
    
    # Verify credentials
    if not verify_admin_credentials(credentials):
        logger.warning(
            f"Failed login attempt for user '{credentials.username}' "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token pair
    tokens = create_token_pair(credentials.username)
    
    logger.info(
        f"✅ User '{credentials.username}' logged in from "
        f"{request.client.host if request.client else 'unknown'}"
    )
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    username: str = Depends(require_refresh_token)
):
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        New token pair with fresh access_token
    """
    # Generate new token pair
    tokens = create_token_pair(username)
    
    logger.info(f"Token refreshed for user: {username}")
    
    return tokens


@router.get("/keys", response_model=List[APIKey])
async def list_api_keys(
    request: Request,
    key_id: str = Depends(require_api_key)
):
    """
    List all API keys (admin only)
    
    Headers:
        X-API-Key: <api_key>
    
    Returns:
        List of API keys (without actual keys)
    """
    keys = api_key_manager.list_keys()
    logger.info(f"Listed {len(keys)} API keys")
    return keys


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: Request,
    key_data: APIKeyCreate,
    key_id: str = Depends(require_api_key)
):
    """
    Create a new API key (admin only)
    
    Headers:
        X-API-Key: <api_key>
    
    Body:
        {
            "name": "My Service",
            "description": "API key for service X"
        }
    
    Returns:
        API key details including the actual key (shown only once!)
    
    ⚠️  IMPORTANT: Save the API key immediately. It will not be shown again!
    """
    # Apply rate limiting
    admin_rate_limiter.check_rate_limit(request, endpoint="create_api_key")
    
    api_key_response = api_key_manager.generate_key(
        name=key_data.name,
        description=key_data.description
    )
    
    logger.info(
        f"Created API key '{key_data.name}' (ID: {api_key_response.key_id}) "
        f"by key {key_id}"
    )
    
    return api_key_response


@router.post("/keys/{target_key_id}/revoke")
async def revoke_api_key(
    request: Request,
    target_key_id: str,
    key_id: str = Depends(require_api_key)
):
    """
    Revoke (disable) an API key
    
    Headers:
        X-API-Key: <api_key>
    
    Returns:
        Success message
    """
    if not api_key_manager.revoke_key(target_key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {target_key_id}"
        )
    
    logger.info(f"Revoked API key {target_key_id} by key {key_id}")
    
    return {
        "message": f"API key {target_key_id} revoked successfully",
        "key_id": target_key_id
    }


@router.delete("/keys/{target_key_id}")
async def delete_api_key(
    request: Request,
    target_key_id: str,
    key_id: str = Depends(require_api_key)
):
    """
    Permanently delete an API key
    
    Headers:
        X-API-Key: <api_key>
    
    Returns:
        Success message
    """
    if not api_key_manager.delete_key(target_key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {target_key_id}"
        )
    
    logger.info(f"Deleted API key {target_key_id} by key {key_id}")
    
    return {
        "message": f"API key {target_key_id} deleted successfully",
        "key_id": target_key_id
    }

