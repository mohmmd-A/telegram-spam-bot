"""
خدمة تحديد معدل الطلبات لمنع الإساءة
Rate Limiting Service to Prevent Abuse
"""

import logging
import time
from typing import Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """خدمة تحديد معدل الطلبات"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[int, list] = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make request"""
        current_time = time.time()
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.time_window
        ]
        
        # Check if limit exceeded
        if len(self.requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        self.requests[user_id].append(current_time)
        return True
    
    def get_remaining_requests(self, user_id: int) -> int:
        """Get remaining requests for user"""
        current_time = time.time()
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.time_window
        ]
        
        return max(0, self.max_requests - len(self.requests[user_id]))
    
    def reset_user(self, user_id: int) -> None:
        """Reset rate limit for user"""
        if user_id in self.requests:
            del self.requests[user_id]
            logger.info(f"تم إعادة تعيين حد المعدل للمستخدم {user_id}")
    
    def reset_all(self) -> None:
        """Reset all rate limits"""
        self.requests.clear()
        logger.info("تم إعادة تعيين جميع حدود المعدل")


# Global rate limiter instances
message_rate_limiter = RateLimiter(max_requests=30, time_window=60)  # 30 messages per minute
command_rate_limiter = RateLimiter(max_requests=10, time_window=60)  # 10 commands per minute
