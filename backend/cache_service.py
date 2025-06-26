"""
Redis Caching Service for Performance Optimization
Implements smart caching for frequently accessed data
"""

import redis
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
from functools import wraps
import os

logger = logging.getLogger(__name__)

class CacheService:
    """
    High-performance caching service with Redis backend
    """
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=int(os.environ.get('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("✅ Redis cache service initialized successfully")
        except Exception as e:
            self.available = False
            logger.warning(f"❌ Redis cache service unavailable: {e}")
            # Fallback to in-memory cache
            self._memory_cache = {}
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from function arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.available:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # Use memory cache fallback
                cache_entry = self._memory_cache.get(key)
                if cache_entry and cache_entry['expires'] > datetime.utcnow():
                    return cache_entry['data']
                elif cache_entry:
                    # Remove expired entry
                    del self._memory_cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expiry_seconds: int = 300) -> bool:
        """Set value in cache with expiry"""
        try:
            if self.available:
                return self.redis_client.setex(
                    key, 
                    expiry_seconds, 
                    json.dumps(value, default=str)
                )
            else:
                # Use memory cache fallback
                self._memory_cache[key] = {
                    'data': value,
                    'expires': datetime.utcnow() + timedelta(seconds=expiry_seconds)
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.available:
                return bool(self.redis_client.delete(key))
            else:
                return bool(self._memory_cache.pop(key, None))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.available:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Clear memory cache with pattern
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

# Global cache service instance
cache_service = CacheService()

def cached(expiry_seconds: int = 300, key_prefix: str = "default"):
    """
    Decorator for caching function results
    
    Args:
        expiry_seconds: Cache expiry time in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service._generate_cache_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, expiry_seconds)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service._generate_cache_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, expiry_seconds)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Specific caching functions for Oil & Gas Finder

@cached(expiry_seconds=300, key_prefix="market_data")
async def get_cached_market_data(commodity: str) -> Dict[str, Any]:
    """Cache market data for 5 minutes"""
    # This would typically fetch from external API
    return {
        "commodity": commodity,
        "price": 75.50,
        "change": 0.5,
        "volume": 1000000,
        "timestamp": datetime.utcnow().isoformat()
    }

@cached(expiry_seconds=600, key_prefix="listings")
def get_cached_listings(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Cache listing search results for 10 minutes"""
    # This would typically query the database
    return []

@cached(expiry_seconds=1800, key_prefix="analytics")
def get_cached_analytics(user_id: str, date_range: str) -> Dict[str, Any]:
    """Cache analytics data for 30 minutes"""
    return {
        "user_id": user_id,
        "page_views": 150,
        "engagement_rate": 0.65,
        "date_range": date_range
    }

@cached(expiry_seconds=3600, key_prefix="company_profile")
def get_cached_company_profile(company_id: str) -> Dict[str, Any]:
    """Cache company profiles for 1 hour"""
    return {
        "company_id": company_id,
        "name": "Example Oil Company",
        "description": "Leading oil trading company",
        "trading_hubs": ["Houston", "Singapore"]
    }

# Cache warming functions
class CacheWarmer:
    """
    Proactive cache warming for frequently accessed data
    """
    
    @staticmethod
    async def warm_market_data():
        """Pre-warm market data cache"""
        commodities = ['crude_oil', 'natural_gas', 'lng', 'gasoline', 'diesel']
        for commodity in commodities:
            try:
                await get_cached_market_data(commodity)
                logger.info(f"Warmed market data cache for {commodity}")
            except Exception as e:
                logger.error(f"Failed to warm cache for {commodity}: {e}")
    
    @staticmethod
    def warm_popular_listings():
        """Pre-warm popular listing combinations"""
        popular_filters = [
            {"commodity": "crude_oil"},
            {"commodity": "natural_gas"},
            {"location": "houston"},
            {"location": "singapore"},
            {}  # All listings
        ]
        
        for filters in popular_filters:
            try:
                get_cached_listings(filters)
                logger.info(f"Warmed listings cache for filters: {filters}")
            except Exception as e:
                logger.error(f"Failed to warm listings cache: {e}")

# Cache invalidation helpers
class CacheInvalidator:
    """
    Smart cache invalidation when data changes
    """
    
    @staticmethod
    def invalidate_user_cache(user_id: str):
        """Invalidate all cache entries for a specific user"""
        patterns = [
            f"*user:{user_id}*",
            f"*analytics:{user_id}*",
            f"*profile:{user_id}*"
        ]
        
        for pattern in patterns:
            cache_service.clear_pattern(pattern)
        
        logger.info(f"Invalidated cache for user: {user_id}")
    
    @staticmethod
    def invalidate_listings_cache():
        """Invalidate listings cache when new listings are added"""
        cache_service.clear_pattern("listings:*")
        logger.info("Invalidated all listings cache")
    
    @staticmethod
    def invalidate_market_data_cache(commodity: str = None):
        """Invalidate market data cache"""
        if commodity:
            pattern = f"market_data:*{commodity}*"
        else:
            pattern = "market_data:*"
        
        cache_service.clear_pattern(pattern)
        logger.info(f"Invalidated market data cache for: {commodity or 'all commodities'}")

# Performance monitoring
class CacheMonitor:
    """
    Monitor cache performance and hit rates
    """
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            if cache_service.available:
                info = cache_service.redis_client.info()
                return {
                    "cache_type": "Redis",
                    "connected_clients": info.get('connected_clients', 0),
                    "used_memory": info.get('used_memory_human', '0B'),
                    "hits": info.get('keyspace_hits', 0),
                    "misses": info.get('keyspace_misses', 0),
                    "hit_rate": info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
                }
            else:
                return {
                    "cache_type": "Memory",
                    "entries": len(cache_service._memory_cache),
                    "status": "Fallback mode"
                }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

# Export the main cache service and utilities
__all__ = [
    'cache_service',
    'cached',
    'CacheWarmer',
    'CacheInvalidator',
    'CacheMonitor',
    'get_cached_market_data',
    'get_cached_listings',
    'get_cached_analytics',
    'get_cached_company_profile'
]