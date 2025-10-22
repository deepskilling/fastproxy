"""
Audit API - Endpoints to query audit logs
"""
from fastapi import APIRouter, Request, Query
from typing import Optional, List

from audit.models import AuditEntry

router = APIRouter()


@router.get("/logs", response_model=List[AuditEntry])
async def get_audit_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None),
    client_ip: Optional[str] = Query(None)
):
    """
    Get audit logs with optional filtering
    
    - **limit**: Number of records to return (1-1000)
    - **offset**: Number of records to skip
    - **event_type**: Filter by event type ('request' or 'admin_action')
    - **client_ip**: Filter by client IP address
    """
    audit_logger = request.app.state.audit_logger
    
    logs = audit_logger.get_recent_logs(
        limit=limit,
        offset=offset,
        event_type=event_type,
        client_ip=client_ip
    )
    
    return logs


@router.get("/stats")
async def get_audit_stats(request: Request):
    """
    Get audit log statistics
    """
    audit_logger = request.app.state.audit_logger
    stats = audit_logger.get_stats()
    
    return {
        "status": "success",
        "stats": stats
    }

