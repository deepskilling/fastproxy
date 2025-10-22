"""
Input validation utilities
"""
import ipaddress
import re
from fastapi import HTTPException, status


def validate_ip_address(ip: str) -> str:
    """
    Validate IP address format
    
    Args:
        ip: IP address string to validate
    
    Returns:
        Validated IP address string
    
    Raises:
        HTTPException: If IP address is invalid
    """
    try:
        # This will raise ValueError if invalid
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid IP address format: {ip}"
        )


def validate_event_type(event_type: str) -> str:
    """
    Validate audit event type
    
    Args:
        event_type: Event type to validate
    
    Returns:
        Validated event type
    
    Raises:
        HTTPException: If event type is invalid
    """
    valid_types = ['request', 'admin_action']
    
    if event_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Must be one of: {', '.join(valid_types)}"
        )
    
    return event_type

