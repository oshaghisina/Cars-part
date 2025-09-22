"""
AI Gateway Caching System

This module provides comprehensive caching capabilities for the AI Gateway,
including response caching, query result caching, and intelligent cache invalidation.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached entry with metadata."""

    def __init__(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        created_at: Optional[datetime] = None,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None,
    ):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = created_at or datetime.now()
        self.access_count = access_count
        self.last_accessed = last_accessed or self.created_at
        self.expires_at = self.created_at + timedelta(seconds=ttl)

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        entry = cls(
            key=data["key"],
            value=data["value"],
            ttl=data["ttl"],
            created_at=datetime.fromisoformat(data["created_at"]),
            access_count=data["access_count"],
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
        )
        return entry


class AICacheManager:
    """
    Comprehensive caching manager for AI Gateway operations.
    Supports both in-memory and Redis caching with intelligent eviction policies.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
        max_memory_entries: int = 10000,
        enable_redis: bool = True,
    ):
        self.default_ttl = default_ttl
        self.max_memory_entries = max_memory_entries
        self.enable_redis = enable_redis

        # In-memory cache
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._access_times: List[Tuple[datetime, str]] = []  # For LRU tracking

        # Redis connection
        self._redis_client: Optional[redis.Redis] = None
        if enable_redis and REDIS_AVAILABLE:
            try:
                redis_url = redis_url or getattr(settings, "redis_url", "redis://localhost:6379/0")
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self._redis_client.ping()
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Falling back to memory-only cache.")
                self._redis_client = None
                self.enable_redis = False
        elif enable_redis and not REDIS_AVAILABLE:
            logger.warning("Redis package not available. Using memory-only cache.")
            self.enable_redis = False

        # Cache statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "redis_hits": 0,
            "redis_misses": 0,
            "memory_hits": 0,
            "memory_misses": 0,
        }

    def _generate_cache_key(self, prefix: str, task_type: str, context: Dict[str, Any], **kwargs) -> str:
        """Generate a consistent cache key for the given parameters."""
        # Create a deterministic hash of the context
        context_str = json.dumps(context, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)

        # Combine all parameters
        combined = f"{prefix}:{task_type}:{context_str}:{kwargs_str}"

        # Generate hash
        hash_obj = hashlib.sha256(combined.encode())
        return f"ai_cache:{hash_obj.hexdigest()[:16]}"

    async def get(self, prefix: str, task_type: str, context: Dict[str, Any], **kwargs) -> Optional[Any]:
        """
        Retrieve a cached value.

        Args:
            prefix: Cache key prefix
            task_type: Type of AI task
            context: Context data
            **kwargs: Additional parameters

        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._generate_cache_key(prefix, task_type, context, **kwargs)

        # Try Redis first if available
        if self.enable_redis and self._redis_client:
            try:
                cached_data = self._redis_client.get(cache_key)
                if cached_data:
                    entry_data = json.loads(cached_data)
                    entry = CacheEntry.from_dict(entry_data)

                    if not entry.is_expired():
                        entry.touch()
                        # Update Redis with new access info
                        self._redis_client.setex(cache_key, entry.ttl, json.dumps(entry.to_dict()))

                        self._stats["hits"] += 1
                        self._stats["redis_hits"] += 1
                        logger.debug(f"Cache hit (Redis): {cache_key}")
                        return entry.value
                    else:
                        # Remove expired entry
                        self._redis_client.delete(cache_key)
                        self._stats["misses"] += 1
                        self._stats["redis_misses"] += 1
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        # Try memory cache
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired():
                entry.touch()
                self._stats["hits"] += 1
                self._stats["memory_hits"] += 1
                logger.debug(f"Cache hit (Memory): {cache_key}")
                return entry.value
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                self._stats["misses"] += 1
                self._stats["memory_misses"] += 1

        self._stats["misses"] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return None

    async def set(
        self,
        prefix: str,
        task_type: str,
        context: Dict[str, Any],
        value: Any,
        ttl: Optional[int] = None,
        **kwargs,
    ) -> None:
        """
        Store a value in cache.

        Args:
            prefix: Cache key prefix
            task_type: Type of AI task
            context: Context data
            value: Value to cache
            ttl: Time to live in seconds
            **kwargs: Additional parameters
        """
        cache_key = self._generate_cache_key(prefix, task_type, context, **kwargs)
        ttl = ttl or self.default_ttl

        entry = CacheEntry(key=cache_key, value=value, ttl=ttl)

        # Store in Redis if available
        if self.enable_redis and self._redis_client:
            try:
                self._redis_client.setex(cache_key, ttl, json.dumps(entry.to_dict(), default=str))
                logger.debug(f"Cached in Redis: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        # Store in memory cache
        self._memory_cache[cache_key] = entry
        self._access_times.append((datetime.now(), cache_key))

        # Evict if memory cache is full
        if len(self._memory_cache) > self.max_memory_entries:
            await self._evict_lru()

        logger.debug(f"Cached in memory: {cache_key}")

    async def delete(self, prefix: str, task_type: str, context: Dict[str, Any], **kwargs) -> bool:
        """
        Delete a cached value.

        Args:
            prefix: Cache key prefix
            task_type: Type of AI task
            context: Context data
            **kwargs: Additional parameters

        Returns:
            True if deleted, False if not found
        """
        cache_key = self._generate_cache_key(prefix, task_type, context, **kwargs)
        deleted = False

        # Delete from Redis
        if self.enable_redis and self._redis_client:
            try:
                if self._redis_client.delete(cache_key):
                    deleted = True
                    logger.debug(f"Deleted from Redis: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        # Delete from memory
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
            # Remove from access times
            self._access_times = [(t, k) for t, k in self._access_times if k != cache_key]
            deleted = True
            logger.debug(f"Deleted from memory: {cache_key}")

        return deleted

    async def clear(self, prefix: Optional[str] = None) -> int:
        """
        Clear cache entries.

        Args:
            prefix: Optional prefix to filter by

        Returns:
            Number of entries cleared
        """
        cleared_count = 0

        # Clear Redis
        if self.enable_redis and self._redis_client:
            try:
                if prefix:
                    pattern = f"ai_cache:{prefix}:*"
                    keys = self._redis_client.keys(pattern)
                    if keys:
                        cleared_count += self._redis_client.delete(*keys)
                else:
                    pattern = "ai_cache:*"
                    keys = self._redis_client.keys(pattern)
                    if keys:
                        cleared_count += self._redis_client.delete(*keys)
                logger.info(f"Cleared {cleared_count} entries from Redis")
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

        # Clear memory cache
        if prefix:
            keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(f"ai_cache:{prefix}:")]
            for key in keys_to_delete:
                del self._memory_cache[key]
                cleared_count += 1
        else:
            cleared_count += len(self._memory_cache)
            self._memory_cache.clear()
            self._access_times.clear()

        logger.info(f"Cleared {cleared_count} entries from memory cache")
        return cleared_count

    async def _evict_lru(self) -> None:
        """Evict least recently used entries from memory cache."""
        if not self._access_times:
            return

        # Sort by access time (oldest first)
        self._access_times.sort(key=lambda x: x[0])

        # Remove oldest 10% of entries
        evict_count = max(1, len(self._memory_cache) // 10)
        evicted = 0

        for access_time, cache_key in self._access_times:
            if evicted >= evict_count:
                break

            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
                evicted += 1
                self._stats["evictions"] += 1

        # Clean up access times
        self._access_times = [(t, k) for t, k in self._access_times if k in self._memory_cache]

        logger.debug(f"Evicted {evicted} LRU entries from memory cache")

    async def cleanup_expired(self) -> int:
        """Remove expired entries from memory cache."""
        expired_keys = []
        datetime.now()

        for cache_key, entry in self._memory_cache.items():
            if entry.is_expired():
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            del self._memory_cache[cache_key]

        # Clean up access times
        self._access_times = [(t, k) for t, k in self._access_times if k in self._memory_cache]

        logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "redis_hits": self._stats["redis_hits"],
            "redis_misses": self._stats["redis_misses"],
            "memory_hits": self._stats["memory_hits"],
            "memory_misses": self._stats["memory_misses"],
            "evictions": self._stats["evictions"],
            "memory_entries": len(self._memory_cache),
            "redis_enabled": self.enable_redis,
            "max_memory_entries": self.max_memory_entries,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache systems."""
        health = {"memory_cache": "healthy", "redis_cache": "unavailable", "overall": "degraded"}

        # Check memory cache
        try:
            # Test memory cache operations
            test_key = "health_check_test"
            test_value = {"test": True, "timestamp": datetime.now().isoformat()}

            self._memory_cache[test_key] = CacheEntry(key=test_key, value=test_value, ttl=1)

            if test_key in self._memory_cache:
                del self._memory_cache[test_key]
                health["memory_cache"] = "healthy"
            else:
                health["memory_cache"] = "unhealthy"
        except Exception as e:
            health["memory_cache"] = "unhealthy"
            logger.error(f"Memory cache health check failed: {e}")

        # Check Redis cache
        if self.enable_redis and self._redis_client:
            try:
                self._redis_client.ping()
                health["redis_cache"] = "healthy"
            except Exception as e:
                health["redis_cache"] = "unhealthy"
                logger.error(f"Redis cache health check failed: {e}")

        # Determine overall health
        if health["memory_cache"] == "healthy" and health["redis_cache"] == "healthy":
            health["overall"] = "healthy"
        elif health["memory_cache"] == "healthy":
            health["overall"] = "degraded"
        else:
            health["overall"] = "unhealthy"

        return health


# Global cache manager instance
cache_manager = AICacheManager(enable_redis=REDIS_AVAILABLE)


class CacheDecorator:
    """Decorator for caching AI operations."""

    def __init__(self, prefix: str = "ai_operation", ttl: int = 3600, cache_manager: AICacheManager = None):
        self.prefix = prefix
        self.ttl = ttl
        self.cache_manager = cache_manager or globals()["cache_manager"]

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Extract context from function arguments
            context = {}
            if args:
                context["args"] = [str(arg) for arg in args]
            if kwargs:
                context["kwargs"] = kwargs

            # Try to get from cache
            cached_result = await self.cache_manager.get(self.prefix, func.__name__, context, **kwargs)

            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)

            await self.cache_manager.set(self.prefix, func.__name__, context, result, ttl=self.ttl, **kwargs)

            logger.debug(f"Cached result for {func.__name__}")
            return result

        return wrapper


def cache_ai_operation(prefix: str = "ai_operation", ttl: int = 3600):
    """Decorator for caching AI operations."""
    return CacheDecorator(prefix=prefix, ttl=ttl)
