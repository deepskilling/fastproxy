"""
Models - SQLite schema for audit log entries
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditEntry(BaseModel):
    """
    Audit log entry model
    """
    id: Optional[int] = None
    timestamp: datetime
    event_type: str  # 'request' or 'admin_action'
    client_ip: str
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    action: Optional[str] = None  # For admin actions
    details: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuditQueryParams(BaseModel):
    """
    Query parameters for fetching audit logs
    """
    limit: int = 100
    offset: int = 0
    event_type: Optional[str] = None
    client_ip: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# SQLite schema
AUDIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    method TEXT,
    path TEXT,
    status_code INTEGER,
    duration_ms REAL,
    action TEXT,
    details TEXT,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_client_ip ON audit_log(client_ip);
"""

