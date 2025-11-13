"""
Rate limiting middleware for API protection
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting based on IP address"""
    
    def __init__(self, requests_per_minute: int = 20, requests_per_hour: int = 100):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Storage: {ip: [(timestamp, endpoint), ...]}
        self.request_log = defaultdict(list)
        
        # Blocked IPs: {ip: unblock_time}
        self.blocked_ips = {}
    
    def _clean_old_requests(self, ip: str):
        """Remove requests older than 1 hour"""
        if ip not in self.request_log:
            return
        
        cutoff_time = time.time() - 3600  # 1 hour ago
        self.request_log[ip] = [
            (ts, endpoint) for ts, endpoint in self.request_log[ip]
            if ts > cutoff_time
        ]
    
    def _is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        if ip in self.blocked_ips:
            unblock_time = self.blocked_ips[ip]
            if time.time() < unblock_time:
                return True
            else:
                # Unblock
                del self.blocked_ips[ip]
                return False
        return False
    
    def _block_ip(self, ip: str, duration_minutes: int = 15):
        """Block IP for specified duration"""
        unblock_time = time.time() + (duration_minutes * 60)
        self.blocked_ips[ip] = unblock_time
        logger.warning(f"Blocked IP {ip} for {duration_minutes} minutes")
    
    def check_rate_limit(self, ip: str, endpoint: str) -> dict:
        """
        Check if request should be allowed
        
        Args:
            ip: Client IP address
            endpoint: API endpoint
            
        Returns:
            Dictionary with allowed status and metadata
        """
        # Check if blocked
        if self._is_blocked(ip):
            remaining_time = int(self.blocked_ips[ip] - time.time())
            logger.warning(f"Blocked IP {ip} attempted access")
            return {
                'allowed': False,
                'reason': 'temporarily_blocked',
                'retry_after': remaining_time
            }
        
        # Clean old requests
        self._clean_old_requests(ip)
        
        current_time = time.time()
        
        # Add current request
        self.request_log[ip].append((current_time, endpoint))
        
        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = [
            ts for ts, _ in self.request_log[ip]
            if ts > minute_ago
        ]
        
        if len(recent_requests) > self.requests_per_minute:
            self._block_ip(ip, duration_minutes=5)
            return {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'limit': 'per_minute',
                'retry_after': 300  # 5 minutes
            }
        
        # Check hour limit
        hour_ago = current_time - 3600
        hourly_requests = [
            ts for ts, _ in self.request_log[ip]
            if ts > hour_ago
        ]
        
        if len(hourly_requests) > self.requests_per_hour:
            self._block_ip(ip, duration_minutes=15)
            return {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'limit': 'per_hour',
                'retry_after': 900  # 15 minutes
            }
        
        # Allowed
        return {
            'allowed': True,
            'requests_remaining_minute': self.requests_per_minute - len(recent_requests),
            'requests_remaining_hour': self.requests_per_hour - len(hourly_requests)
        }
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        total_ips = len(self.request_log)
        blocked_ips = len(self.blocked_ips)
        
        return {
            'total_ips': total_ips,
            'blocked_ips': blocked_ips,
            'requests_per_minute_limit': self.requests_per_minute,
            'requests_per_hour_limit': self.requests_per_hour
        }


# Global rate limiter
rate_limiter = RateLimiter(requests_per_minute=20, requests_per_hour=100)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded IP (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"
