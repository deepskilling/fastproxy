"""
Rate Limiter - Simple IP-based rate limiting
"""
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    IP-based rate limiter using sliding window algorithm
    """
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        # Store: {ip: [(timestamp1, ), (timestamp2, ), ...]}
        self.request_log: Dict[str, list] = defaultdict(list)
    
    def allow_request(self, client_ip: str) -> bool:
        """
        Check if request should be allowed based on rate limit
        
        Args:
            client_ip: Client IP address
        
        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()
        
        # Get request history for this IP
        request_times = self.request_log[client_ip]
        
        # Remove requests outside the window
        cutoff_time = current_time - self.window_size
        request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Check if under limit
        if len(request_times) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(request_times)} requests")
            return False
        
        # Add current request
        request_times.append(current_time)
        return True
    
    def get_stats(self, client_ip: str) -> Dict:
        """
        Get rate limit stats for an IP
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        request_times = self.request_log.get(client_ip, [])
        recent_requests = [t for t in request_times if t > cutoff_time]
        
        return {
            "ip": client_ip,
            "requests_in_window": len(recent_requests),
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - len(recent_requests))
        }
    
    def update_limit(self, requests_per_minute: int):
        """
        Update rate limit threshold
        """
        self.requests_per_minute = requests_per_minute
        logger.info(f"Rate limit updated to {requests_per_minute} requests/minute")
    
    def clear_ip(self, client_ip: str):
        """
        Clear rate limit history for specific IP
        """
        if client_ip in self.request_log:
            del self.request_log[client_ip]
            logger.info(f"Cleared rate limit for {client_ip}")
    
    def cleanup(self):
        """
        Periodic cleanup of old entries
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        for ip in list(self.request_log.keys()):
            request_times = self.request_log[ip]
            request_times[:] = [t for t in request_times if t > cutoff_time]
            
            # Remove empty entries
            if not request_times:
                del self.request_log[ip]

