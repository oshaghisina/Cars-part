"""
AI Gateway Resource Management

This module provides comprehensive resource management for the AI Gateway,
including connection pooling, resource limits, and adaptive scaling.
"""

import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


class ResourcePool:
    """Manages a pool of resources with automatic scaling and health monitoring."""

    def __init__(
        self,
        resource_type: str,
        min_size: int = 1,
        max_size: int = 10,
        initial_size: int = 2,
        idle_timeout: int = 300,
        health_check_interval: int = 60,
    ):
        self.resource_type = resource_type
        self.min_size = min_size
        self.max_size = max_size
        self.initial_size = initial_size
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval

        self.pool: List[Any] = []
        self.available: Set[Any] = set()
        self.in_use: Set[Any] = set()
        self.unhealthy: Set[Any] = set()

        self.creation_times: Dict[Any, datetime] = {}
        self.last_used: Dict[Any, datetime] = {}
        self.usage_count: Dict[Any, int] = defaultdict(int)

        self.total_created = 0
        self.total_destroyed = 0
        self.total_requests = 0
        self.total_errors = 0

        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # Initialize pool lazily
        self._initialized = False

    async def _initialize_pool(self):
        """Initialize the resource pool with initial resources."""
        async with self._lock:
            for _ in range(self.initial_size):
                await self._create_resource()

            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _create_resource(self) -> Any:
        """Create a new resource instance."""
        try:
            # This would be implemented based on the specific resource type
            # For now, we'll create a mock resource
            resource = {
                "id": f"{self.resource_type}_{self.total_created}",
                "created_at": datetime.now(),
                "status": "healthy",
            }

            self.pool.append(resource)
            self.available.add(resource)
            self.creation_times[resource] = datetime.now()
            self.total_created += 1

            logger.debug(f"Created {self.resource_type} resource: {resource['id']}")
            return resource

        except Exception as e:
            logger.error(f"Failed to create {self.resource_type} resource: {e}")
            raise

    async def _destroy_resource(self, resource: Any):
        """Destroy a resource instance."""
        try:
            if resource in self.pool:
                self.pool.remove(resource)

            self.available.discard(resource)
            self.in_use.discard(resource)
            self.unhealthy.discard(resource)

            self.creation_times.pop(resource, None)
            self.last_used.pop(resource, None)
            self.usage_count.pop(resource, None)

            self.total_destroyed += 1
            logger.debug(
                f"Destroyed {self.resource_type} resource: {resource.get('id', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to destroy {self.resource_type} resource: {e}")

    async def _ensure_initialized(self):
        """Ensure the pool is initialized."""
        if not self._initialized:
            await self._initialize_pool()
            self._initialized = True

    async def acquire(self, timeout: float = 30.0) -> Any:
        """
        Acquire a resource from the pool.

        Args:
            timeout: Maximum time to wait for a resource

        Returns:
            Resource instance

        Raises:
            TimeoutError: If no resource is available within timeout
        """
        await self._ensure_initialized()
        start_time = time.time()

        while time.time() - start_time < timeout:
            async with self._lock:
                # Try to get an available resource
                if self.available:
                    resource = self.available.pop()
                    self.in_use.add(resource)
                    self.last_used[resource] = datetime.now()
                    self.usage_count[resource] += 1
                    self.total_requests += 1

                    logger.debug(
                        f"Acquired {self.resource_type} resource: {resource.get('id', 'unknown')}")
                    return resource

                # Try to create a new resource if under max size
                if len(self.pool) < self.max_size:
                    try:
                        resource = await self._create_resource()
                        self.available.remove(resource)
                        self.in_use.add(resource)
                        self.last_used[resource] = datetime.now()
                        self.usage_count[resource] += 1
                        self.total_requests += 1

                        logger.debug(
                            f"Created and acquired {self.resource_type} resource: {resource.get('id', 'unknown')}")
                        return resource
                    except Exception as e:
                        logger.error(f"Failed to create new resource: {e}")
                        self.total_errors += 1

            # Wait before retrying
            await asyncio.sleep(0.1)

        raise TimeoutError(f"No {self.resource_type} resources available within {timeout} seconds")

    async def release(self, resource: Any, mark_unhealthy: bool = False):
        """
        Release a resource back to the pool.

        Args:
            resource: Resource to release
            mark_unhealthy: Whether to mark the resource as unhealthy
        """
        await self._ensure_initialized()
        async with self._lock:
            if resource in self.in_use:
                self.in_use.remove(resource)

                if mark_unhealthy:
                    self.unhealthy.add(resource)
                    logger.warning(
                        f"Marked {self.resource_type} resource as unhealthy: {resource.get('id', 'unknown')}")
                else:
                    self.available.add(resource)
                    logger.debug(
                        f"Released {self.resource_type} resource: {resource.get('id', 'unknown')}")
            else:
                logger.warning(
                    f"Attempted to release resource not in use: {resource.get('id', 'unknown')}")

    async def _health_check_loop(self):
        """Background task for health checking resources."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._health_check_all()
            except Exception as e:
                logger.error(f"Health check loop error: {e}")

    async def _health_check_all(self):
        """Check health of all resources in the pool."""
        async with self._lock:
            for resource in list(self.pool):
                try:
                    is_healthy = await self._check_resource_health(resource)
                    if not is_healthy:
                        self.unhealthy.add(resource)
                        self.available.discard(resource)
                        self.in_use.discard(resource)
                        logger.warning(
                            f"Resource failed health check: {
                                resource.get(
                                    'id', 'unknown')}")
                except Exception as e:
                    logger.error(f"Health check failed for resource: {e}")
                    self.unhealthy.add(resource)

    async def _check_resource_health(self, resource: Any) -> bool:
        """Check if a specific resource is healthy."""
        # This would be implemented based on the specific resource type
        # For now, we'll do a simple check
        try:
            # Mock health check - in practice, this would ping the resource
            return resource.get("status") == "healthy"
        except Exception:
            return False

    async def _cleanup_loop(self):
        """Background task for cleaning up idle and unhealthy resources."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_resources()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _cleanup_resources(self):
        """Clean up idle and unhealthy resources."""
        async with self._lock:
            current_time = datetime.now()

            # Remove unhealthy resources
            for resource in list(self.unhealthy):
                await self._destroy_resource(resource)

            # Remove idle resources (if above min size)
            for resource in list(self.available):
                if (
                    len(self.pool) > self.min_size
                    and resource in self.last_used
                    and current_time - self.last_used[resource] > timedelta(seconds=self.idle_timeout)
                ):
                    await self._destroy_resource(resource)

    def get_stats(self) -> Dict[str, Any]:
        """Get resource pool statistics."""
        if not self._initialized:
            return {
                "resource_type": self.resource_type,
                "pool_size": 0,
                "available": 0,
                "in_use": 0,
                "unhealthy": 0,
                "min_size": self.min_size,
                "max_size": self.max_size,
                "total_created": 0,
                "total_destroyed": 0,
                "total_requests": 0,
                "total_errors": 0,
                "utilization_rate": 0,
            }
        return {
            "resource_type": self.resource_type,
            "pool_size": len(self.pool),
            "available": len(self.available),
            "in_use": len(self.in_use),
            "unhealthy": len(self.unhealthy),
            "min_size": self.min_size,
            "max_size": self.max_size,
            "total_created": self.total_created,
            "total_destroyed": self.total_destroyed,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "utilization_rate": len(self.in_use) / max(len(self.pool), 1) * 100,
        }

    async def shutdown(self):
        """Shutdown the resource pool and cleanup all resources."""
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        async with self._lock:
            for resource in list(self.pool):
                await self._destroy_resource(resource)

        logger.info(f"Shutdown {self.resource_type} resource pool")


class ConnectionManager:
    """Manages database and external service connections with pooling."""

    def __init__(self):
        self.pools: Dict[str, ResourcePool] = {}
        self.connection_configs = self._load_connection_configs()
        self._initialize_pools()

    def _load_connection_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load connection configurations from settings."""
        return {
            "database": {
                "min_size": getattr(settings, "db_pool_min_size", 1),
                "max_size": getattr(settings, "db_pool_max_size", 10),
                "initial_size": getattr(settings, "db_pool_initial_size", 2),
                "idle_timeout": getattr(settings, "db_pool_idle_timeout", 300),
            },
            "redis": {
                "min_size": getattr(settings, "redis_pool_min_size", 1),
                "max_size": getattr(settings, "redis_pool_max_size", 5),
                "initial_size": getattr(settings, "redis_pool_initial_size", 1),
                "idle_timeout": getattr(settings, "redis_pool_idle_timeout", 300),
            },
            "openai": {
                "min_size": getattr(settings, "openai_pool_min_size", 1),
                "max_size": getattr(settings, "openai_pool_max_size", 3),
                "initial_size": getattr(settings, "openai_pool_initial_size", 1),
                "idle_timeout": getattr(settings, "openai_pool_idle_timeout", 600),
            },
        }

    def _initialize_pools(self):
        """Initialize connection pools for all configured services."""
        for service_name, config in self.connection_configs.items():
            self.pools[service_name] = ResourcePool(resource_type=service_name, **config)
            logger.info(f"Initialized {service_name} connection pool")

    async def get_connection(self, service_name: str, timeout: float = 30.0) -> Any:
        """Get a connection from the specified service pool."""
        if service_name not in self.pools:
            raise ValueError(f"Unknown service: {service_name}")

        return await self.pools[service_name].acquire(timeout)

    async def release_connection(
            self,
            service_name: str,
            connection: Any,
            mark_unhealthy: bool = False):
        """Release a connection back to the service pool."""
        if service_name not in self.pools:
            logger.warning(f"Attempted to release connection for unknown service: {service_name}")
            return

        await self.pools[service_name].release(connection, mark_unhealthy)

    def get_pool_stats(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for connection pools."""
        if service_name:
            if service_name not in self.pools:
                return {}
            return self.pools[service_name].get_stats()

        return {service: pool.get_stats() for service, pool in self.pools.items()}

    async def shutdown(self):
        """Shutdown all connection pools."""
        for pool in self.pools.values():
            await pool.shutdown()
        logger.info("All connection pools shutdown")


class ResourceLimiter:
    """Enforces resource limits and prevents resource exhaustion."""

    def __init__(self):
        self.limits = {
            "max_concurrent_requests": getattr(settings, "ai_max_concurrent_requests", 100),
            "max_requests_per_minute": getattr(settings, "ai_max_requests_per_minute", 1000),
            "max_tokens_per_minute": getattr(settings, "ai_max_tokens_per_minute", 100000),
            "max_cost_per_hour": getattr(settings, "ai_max_cost_per_hour", 100.0),
            "max_memory_usage_mb": getattr(settings, "ai_max_memory_usage_mb", 1024),
        }

        self.current_usage = {
            "concurrent_requests": 0,
            "requests_this_minute": 0,
            "tokens_this_minute": 0,
            "cost_this_hour": 0.0,
            "memory_usage_mb": 0,
        }

        self.request_times: List[datetime] = []
        self.token_usage_times: List[Tuple[datetime, int]] = []
        self.cost_usage_times: List[Tuple[datetime, float]] = []

        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure the resource limiter is initialized."""
        if not self._initialized:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._initialized = True

    async def check_limits(self, request_tokens: int = 0,
                           estimated_cost: float = 0.0) -> Tuple[bool, Optional[str]]:
        """
        Check if a request can be processed within resource limits.

        Args:
            request_tokens: Estimated tokens for the request
            estimated_cost: Estimated cost for the request

        Returns:
            Tuple of (allowed, reason_if_denied)
        """
        async with self._lock:
            # Check concurrent request limit
            if self.current_usage["concurrent_requests"] >= self.limits["max_concurrent_requests"]:
                return False, "Maximum concurrent requests exceeded"

            # Check requests per minute limit
            current_time = datetime.now()
            minute_ago = current_time - timedelta(minutes=1)
            recent_requests = [t for t in self.request_times if t > minute_ago]

            if len(recent_requests) >= self.limits["max_requests_per_minute"]:
                return False, "Maximum requests per minute exceeded"

            # Check tokens per minute limit
            recent_tokens = sum(tokens for t, tokens in self.token_usage_times if t > minute_ago)
            if recent_tokens + request_tokens > self.limits["max_tokens_per_minute"]:
                return False, "Maximum tokens per minute exceeded"

            # Check cost per hour limit
            hour_ago = current_time - timedelta(hours=1)
            recent_cost = sum(cost for t, cost in self.cost_usage_times if t > hour_ago)
            if recent_cost + estimated_cost > self.limits["max_cost_per_hour"]:
                return False, "Maximum cost per hour exceeded"

            return True, None

    async def record_request(self, tokens_used: int = 0, actual_cost: float = 0.0):
        """Record a completed request for usage tracking."""
        await self._ensure_initialized()
        async with self._lock:
            current_time = datetime.now()

            self.request_times.append(current_time)
            if tokens_used > 0:
                self.token_usage_times.append((current_time, tokens_used))
            if actual_cost > 0:
                self.cost_usage_times.append((current_time, actual_cost))

    async def acquire_request_slot(self) -> bool:
        """Acquire a slot for a new request."""
        await self._ensure_initialized()
        async with self._lock:
            if self.current_usage["concurrent_requests"] >= self.limits["max_concurrent_requests"]:
                return False

            self.current_usage["concurrent_requests"] += 1
            return True

    async def release_request_slot(self):
        """Release a request slot."""
        await self._ensure_initialized()
        async with self._lock:
            if self.current_usage["concurrent_requests"] > 0:
                self.current_usage["concurrent_requests"] -= 1

    async def _cleanup_loop(self):
        """Background task for cleaning up old usage data."""
        while True:
            try:
                await asyncio.sleep(60)  # Clean up every minute
                await self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Resource limiter cleanup error: {e}")

    async def _cleanup_old_data(self):
        """Remove old usage data to prevent memory leaks."""
        async with self._lock:
            current_time = datetime.now()
            hour_ago = current_time - timedelta(hours=1)

            # Clean up old request times
            self.request_times = [t for t in self.request_times if t > hour_ago]

            # Clean up old token usage
            self.token_usage_times = [(t, tokens)
                                      for t, tokens in self.token_usage_times if t > hour_ago]

            # Clean up old cost usage
            self.cost_usage_times = [(t, cost) for t, cost in self.cost_usage_times if t > hour_ago]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)
        hour_ago = current_time - timedelta(hours=1)

        recent_requests = len([t for t in self.request_times if t > minute_ago])
        recent_tokens = sum(tokens for t, tokens in self.token_usage_times if t > minute_ago)
        recent_cost = sum(cost for t, cost in self.cost_usage_times if t > hour_ago)

        return {
            "limits": self.limits,
            "current_usage": {
                "concurrent_requests": self.current_usage["concurrent_requests"],
                "requests_this_minute": recent_requests,
                "tokens_this_minute": recent_tokens,
                "cost_this_hour": recent_cost,
            },
            "utilization": {
                "concurrent_requests": (
                    self.current_usage["concurrent_requests"] /
                    self.limits["max_concurrent_requests"]) *
                100,
                "requests_per_minute": (
                    recent_requests /
                    self.limits["max_requests_per_minute"]) *
                100,
                "tokens_per_minute": (
                    recent_tokens /
                    self.limits["max_tokens_per_minute"]) *
                100,
                "cost_per_hour": (
                    recent_cost /
                    self.limits["max_cost_per_hour"]) *
                100,
            },
        }

    async def shutdown(self):
        """Shutdown the resource limiter."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("Resource limiter shutdown")


# Global resource management instances
connection_manager = ConnectionManager()
resource_limiter = ResourceLimiter()
