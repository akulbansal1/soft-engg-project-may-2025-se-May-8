import redis
import json
from typing import Any, Optional
from src.core.config import settings

# Redis client for caching
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class Cache:
    """Simple Redis cache wrapper with JSON support"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, expiry: int = 3600) -> bool:
        """Set value in cache with expiry in seconds"""
        try:
            json_value = json.dumps(value, default=str)
            return redis_client.setex(key, expiry, json_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
