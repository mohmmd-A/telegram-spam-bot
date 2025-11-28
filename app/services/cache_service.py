"""
خدمة التخزين المؤقت لتحسين الأداء
Caching Service for Performance Optimization
"""

import logging
import time
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """خدمة التخزين المؤقت"""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


def cached(ttl: int = 3600):
    """Decorator for caching function results"""
    cache = CacheService(ttl=ttl)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            logger.debug(f"Cache miss for {func.__name__}")
            
            return result
        
        return wrapper
    
    return decorator


# Global cache instance
global_cache = CacheService(ttl=3600)
