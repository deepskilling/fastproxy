"""
Admin Rate Limiter - Prevent brute force attacks on admin endpoints
"""
import time
import logging
from collections import defaultdict
from typing import Dict
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class AdminRateLimiter:
    """
    Rate limiter specifically for admin/audit endpoints
    More strict than general rate limiting
    """
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 5):
        """
        Args:
            max_attempts: Maximum login/admin attempts allowed
            window_minutes: Time window in minutes
        """
        self.max_attempts = max_attempts
        self.window_size = window_minutes * 60  # Convert to seconds
        self.attempts: Dict[str, list] = defaultdict(list)
        self.blocked_until: Dict[str, float] = {}
    
    def check_rate_limit(self, request: Request, endpoint: str = "admin") -> bool:
        """
        Check if request should be allowed
        
        Args:
            request: FastAPI Request object
            endpoint: Endpoint identifier for logging
        
        Returns:
            True if allowed, raises HTTPException if blocked
        """
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Check if IP is currently blocked
        if client_ip in self.blocked_until:
            if current_time < self.blocked_until[client_ip]:
                remaining = int(self.blocked_until[client_ip] - current_time)
                logger.warning(
                    f"Blocked {endpoint} request from {client_ip} "
                    f"(blocked for {remaining}s more)"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many attempts. Try again in {remaining} seconds.",
                    headers={"Retry-After": str(remaining)}
                )
            else:
                # Block expired, remove it
                del self.blocked_until[client_ip]
                self.attempts[client_ip] = []
        
        # Get attempt history
        attempt_times = self.attempts[client_ip]
        
        # Remove old attempts outside the window
        cutoff_time = current_time - self.window_size
        attempt_times[:] = [t for t in attempt_times if t > cutoff_time]
        
        # Check if exceeded limit
        if len(attempt_times) >= self.max_attempts:
            # Block for double the window size
            block_duration = self.window_size * 2
            self.blocked_until[client_ip] = current_time + block_duration
            
            logger.warning(
                f"Rate limit exceeded for {endpoint} from {client_ip}: "
                f"{len(attempt_times)} attempts in {self.window_size}s. "
                f"Blocked for {block_duration}s"
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Blocked for {int(block_duration)} seconds.",
                headers={"Retry-After": str(int(block_duration))}
            )
        
        # Record this attempt
        attempt_times.append(current_time)
        return True
    
    def get_stats(self, ip: str) -> Dict:
        """Get rate limit stats for an IP"""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        attempt_times = self.attempts.get(ip, [])
        recent_attempts = [t for t in attempt_times if t > cutoff_time]
        
        is_blocked = ip in self.blocked_until and current_time < self.blocked_until[ip]
        blocked_remaining = 0
        if is_blocked:
            blocked_remaining = int(self.blocked_until[ip] - current_time)
        
        return {
            "ip": ip,
            "attempts_in_window": len(recent_attempts),
            "max_attempts": self.max_attempts,
            "remaining_attempts": max(0, self.max_attempts - len(recent_attempts)),
            "is_blocked": is_blocked,
            "blocked_for_seconds": blocked_remaining
        }
    
    def clear_ip(self, ip: str):
        """Clear rate limit history for specific IP"""
        if ip in self.attempts:
            del self.attempts[ip]
        if ip in self.blocked_until:
            del self.blocked_until[ip]
        logger.info(f"Cleared admin rate limit for {ip}")
    
    def update_limit(self, max_attempts: int, window_minutes: int):
        """Update rate limit settings"""
        self.max_attempts = max_attempts
        self.window_size = window_minutes * 60
        logger.info(
            f"Updated admin rate limit: {max_attempts} attempts "
            f"per {window_minutes} minutes"
        )


# Global admin rate limiter instance
admin_rate_limiter = AdminRateLimiter(max_attempts=5, window_minutes=5)

