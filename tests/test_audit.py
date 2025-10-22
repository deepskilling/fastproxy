"""
Tests for audit logging functionality
"""
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from audit.logger import AuditLogger


@pytest.fixture
def audit_logger():
    """Create temporary audit logger for testing"""
    # Create temporary database file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_audit.db")
    
    logger = AuditLogger(db_path=db_path)
    yield logger
    
    # Cleanup
    logger.close()
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except:
        pass


def test_audit_logger_init(audit_logger):
    """Test audit logger initialization"""
    assert audit_logger.conn is not None
    assert Path(audit_logger.db_path).exists()


def test_log_request(audit_logger):
    """Test logging HTTP requests"""
    audit_logger.log_request(
        client_ip="192.168.1.1",
        method="GET",
        path="/api/users",
        status_code=200,
        duration_ms=45.5,
        user_agent="TestClient/1.0"
    )
    
    # Fetch logs
    logs = audit_logger.get_recent_logs(limit=10)
    
    assert len(logs) == 1
    assert logs[0].client_ip == "192.168.1.1"
    assert logs[0].method == "GET"
    assert logs[0].path == "/api/users"
    assert logs[0].status_code == 200
    assert logs[0].duration_ms == 45.5
    assert logs[0].event_type == "request"


def test_log_admin_action(audit_logger):
    """Test logging admin actions"""
    audit_logger.log_admin_action(
        client_ip="192.168.1.100",
        action="config_reload",
        details="Reloaded 3 routes"
    )
    
    # Fetch logs
    logs = audit_logger.get_recent_logs(limit=10)
    
    assert len(logs) == 1
    assert logs[0].client_ip == "192.168.1.100"
    assert logs[0].action == "config_reload"
    assert logs[0].details == "Reloaded 3 routes"
    assert logs[0].event_type == "admin_action"


def test_get_recent_logs_filtering(audit_logger):
    """Test filtering audit logs"""
    # Log multiple entries
    audit_logger.log_request("192.168.1.1", "GET", "/api/users", 200, 10.0)
    audit_logger.log_request("192.168.1.2", "POST", "/api/posts", 201, 20.0)
    audit_logger.log_admin_action("192.168.1.100", "config_reload", "Test")
    
    # Filter by event type
    requests = audit_logger.get_recent_logs(event_type="request")
    assert len(requests) == 2
    assert all(log.event_type == "request" for log in requests)
    
    admin_actions = audit_logger.get_recent_logs(event_type="admin_action")
    assert len(admin_actions) == 1
    assert admin_actions[0].event_type == "admin_action"
    
    # Filter by client IP
    ip_logs = audit_logger.get_recent_logs(client_ip="192.168.1.1")
    assert len(ip_logs) == 1
    assert ip_logs[0].client_ip == "192.168.1.1"


def test_get_recent_logs_pagination(audit_logger):
    """Test pagination of audit logs"""
    # Log 10 entries
    for i in range(10):
        audit_logger.log_request(
            f"192.168.1.{i}",
            "GET",
            f"/api/resource{i}",
            200,
            10.0
        )
    
    # Get first 5
    page1 = audit_logger.get_recent_logs(limit=5, offset=0)
    assert len(page1) == 5
    
    # Get next 5
    page2 = audit_logger.get_recent_logs(limit=5, offset=5)
    assert len(page2) == 5
    
    # Ensure they're different
    assert page1[0].id != page2[0].id


def test_get_stats(audit_logger):
    """Test getting audit statistics"""
    # Log various entries
    for i in range(5):
        audit_logger.log_request(f"192.168.1.{i}", "GET", "/api/test", 200, 10.0)
    
    for i in range(3):
        audit_logger.log_admin_action("192.168.1.100", "test_action", "Test")
    
    stats = audit_logger.get_stats()
    
    assert stats["total_entries"] == 8
    assert stats["request_count"] == 5
    assert stats["admin_action_count"] == 3


def test_multiple_requests_ordering(audit_logger):
    """Test that logs are returned in reverse chronological order"""
    # Log entries with slight delay
    audit_logger.log_request("192.168.1.1", "GET", "/first", 200, 10.0)
    audit_logger.log_request("192.168.1.1", "GET", "/second", 200, 10.0)
    audit_logger.log_request("192.168.1.1", "GET", "/third", 200, 10.0)
    
    logs = audit_logger.get_recent_logs()
    
    # Most recent should be first
    assert logs[0].path == "/third"
    assert logs[1].path == "/second"
    assert logs[2].path == "/first"

