"""
Tests for rate limiting functionality
"""
import pytest
import time
from proxy.rate_limit import RateLimiter


def test_rate_limiter_basic():
    """Test basic rate limiting"""
    limiter = RateLimiter(requests_per_minute=5)
    
    # Should allow first 5 requests
    for i in range(5):
        assert limiter.allow_request("192.168.1.1") is True
    
    # Should block 6th request
    assert limiter.allow_request("192.168.1.1") is False


def test_rate_limiter_different_ips():
    """Test rate limiting for different IPs"""
    limiter = RateLimiter(requests_per_minute=5)
    
    # Each IP should have separate limit
    for i in range(5):
        assert limiter.allow_request("192.168.1.1") is True
        assert limiter.allow_request("192.168.1.2") is True
    
    # Both IPs should be rate limited now
    assert limiter.allow_request("192.168.1.1") is False
    assert limiter.allow_request("192.168.1.2") is False


def test_rate_limiter_window():
    """Test sliding window behavior"""
    limiter = RateLimiter(requests_per_minute=3)
    limiter.window_size = 2  # Use 2 second window for faster testing
    
    # Make 3 requests
    for i in range(3):
        assert limiter.allow_request("192.168.1.1") is True
    
    # Should be rate limited
    assert limiter.allow_request("192.168.1.1") is False
    
    # Wait for window to expire
    time.sleep(2.1)
    
    # Should be allowed again
    assert limiter.allow_request("192.168.1.1") is True


def test_rate_limiter_stats():
    """Test rate limit statistics"""
    limiter = RateLimiter(requests_per_minute=10)
    
    # Make some requests
    for i in range(5):
        limiter.allow_request("192.168.1.1")
    
    stats = limiter.get_stats("192.168.1.1")
    
    assert stats["ip"] == "192.168.1.1"
    assert stats["requests_in_window"] == 5
    assert stats["limit"] == 10
    assert stats["remaining"] == 5


def test_rate_limiter_update_limit():
    """Test updating rate limit"""
    limiter = RateLimiter(requests_per_minute=5)
    
    # Make 5 requests
    for i in range(5):
        assert limiter.allow_request("192.168.1.1") is True
    
    # Should be blocked
    assert limiter.allow_request("192.168.1.1") is False
    
    # Increase limit
    limiter.update_limit(10)
    
    # Should be allowed now
    assert limiter.allow_request("192.168.1.1") is True


def test_rate_limiter_clear_ip():
    """Test clearing rate limit for specific IP"""
    limiter = RateLimiter(requests_per_minute=3)
    
    # Make 3 requests
    for i in range(3):
        limiter.allow_request("192.168.1.1")
    
    # Should be blocked
    assert limiter.allow_request("192.168.1.1") is False
    
    # Clear the IP
    limiter.clear_ip("192.168.1.1")
    
    # Should be allowed again
    assert limiter.allow_request("192.168.1.1") is True


def test_rate_limiter_cleanup():
    """Test cleanup of old entries"""
    limiter = RateLimiter(requests_per_minute=5)
    limiter.window_size = 1  # 1 second window
    
    # Make requests from multiple IPs
    for i in range(3):
        limiter.allow_request(f"192.168.1.{i}")
    
    assert len(limiter.request_log) == 3
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Run cleanup
    limiter.cleanup()
    
    # All entries should be cleaned up
    assert len(limiter.request_log) == 0

