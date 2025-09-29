"""Redis cache service with pattern invalidation and SLA compliance."""

import json
import time
from typing import Any, Dict, List, Optional

import redis
from redis.exceptions import RedisError

from app.core.config import settings


class CacheService:
    """Redis-based cache service with pattern invalidation and SLA compliance."""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.cache_enabled = settings.cache_enabled
        
    def get_part_detail(self, part_id: int) -> Optional[Dict[str, Any]]:
        """Get cached part detail with freshness check."""
        if not self.cache_enabled:
            return None
            
        try:
            cache_key = f"part_detail:{part_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                # Check if data is still fresh (within SLA)
                if self._is_fresh(data, settings.part_detail_freshness_seconds):
                    return data
                else:
                    # Data is stale, remove it
                    self.redis_client.delete(cache_key)
                    
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            
        return None
    
    def set_part_detail(self, part_id: int, data: Dict[str, Any], ttl: int = None) -> bool:
        """Cache part detail with configurable TTL."""
        if not self.cache_enabled:
            return False
            
        try:
            cache_key = f"part_detail:{part_id}"
            ttl = ttl or settings.cache_part_detail_ttl
            
            # Add timestamp for freshness checking
            data['_cached_at'] = time.time()
            
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(data, default=str)
            )
            return True
            
        except (RedisError, TypeError) as e:
            print(f"Cache set error: {e}")
            return False
    
    def get_part_list(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached part list."""
        if not self.cache_enabled:
            return None
            
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                if self._is_fresh(data, settings.cache_part_list_ttl):
                    return data
                else:
                    self.redis_client.delete(cache_key)
                    
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            
        return None
    
    def set_part_list(self, cache_key: str, data: List[Dict[str, Any]], ttl: int = None) -> bool:
        """Cache part list with configurable TTL."""
        if not self.cache_enabled:
            return False
            
        try:
            ttl = ttl or settings.cache_part_list_ttl
            
            # Add timestamp for freshness checking
            cache_data = {
                '_cached_at': time.time(),
                'data': data
            }
            
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(cache_data, default=str)
            )
            return True
            
        except (RedisError, TypeError) as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate_part(self, part_id: int) -> bool:
        """Invalidate specific part and related caches."""
        if not self.cache_enabled:
            return False
            
        try:
            # Direct key deletion for specific part
            self.redis_client.delete(f"part_detail:{part_id}")
            
            # Pattern-based invalidation for related caches
            self._invalidate_pattern(f"part_list:*")
            self._invalidate_pattern(f"search_results:*")
            
            # Pub/Sub notification for distributed invalidation
            self.redis_client.publish("cache_invalidation", json.dumps({
                "type": "part_updated",
                "part_id": part_id,
                "timestamp": time.time()
            }))
            
            return True
            
        except RedisError as e:
            print(f"Cache invalidation error: {e}")
            return False
    
    def invalidate_stock(self, part_id: int) -> bool:
        """Invalidate stock-related caches."""
        if not self.cache_enabled:
            return False
            
        try:
            # Invalidate part detail (includes stock info)
            self.invalidate_part(part_id)
            
            # Invalidate stock-specific caches
            self._invalidate_pattern(f"stock_level:{part_id}")
            self._invalidate_pattern(f"stock_list:*")
            
            # Pub/Sub notification
            self.redis_client.publish("cache_invalidation", json.dumps({
                "type": "stock_updated",
                "part_id": part_id,
                "timestamp": time.time()
            }))
            
            return True
            
        except RedisError as e:
            print(f"Stock cache invalidation error: {e}")
            return False
    
    def _invalidate_pattern(self, pattern: str) -> bool:
        """Pattern-based invalidation using SCAN - WORKS WITH WILDCARDS."""
        try:
            cursor = 0
            keys_to_delete = []
            
            # Collect all matching keys using SCAN
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                keys_to_delete.extend(keys)
                if cursor == 0:
                    break
            
            # Delete all matching keys in batch
            if keys_to_delete:
                self.redis_client.delete(*keys_to_delete)
                
            return True
            
        except RedisError as e:
            print(f"Pattern invalidation error: {e}")
            return False
    
    def _is_fresh(self, data: Dict[str, Any], max_age_seconds: int) -> bool:
        """Check if cached data is still fresh."""
        if '_cached_at' not in data:
            return False
            
        age = time.time() - data['_cached_at']
        return age <= max_age_seconds
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except RedisError as e:
            print(f"Cache stats error: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def clear_all(self) -> bool:
        """Clear all cache data."""
        if not self.cache_enabled:
            return False
            
        try:
            self.redis_client.flushdb()
            return True
        except RedisError as e:
            print(f"Cache clear error: {e}")
            return False


# Global cache service instance
cache_service = CacheService()
