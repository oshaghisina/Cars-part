"""
AI Orchestrator - Central Coordination for AI Operations

This module provides the main orchestration logic for AI operations in the gateway.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.ai_cache import cache_ai_operation, cache_manager
from app.services.ai_client import AIClient
from app.services.ai_context import AIContextBuilder
from app.services.ai_fallback_manager import AIFallbackManager
from app.services.ai_hybrid_search import HybridSearchEngine
from app.services.ai_language_processor import LanguageProcessor
from app.services.ai_metrics import AIMetricsCollector
from app.services.ai_normalizer import AINormalizer
from app.services.ai_performance import performance_monitor
from app.services.ai_policy_engine import AIPolicyEngine
from app.services.ai_provider import TaskType
from app.services.ai_query_processor import AIQueryProcessor
from app.services.ai_recommendations import AIRecommendationsEngine
from app.services.ai_resource_manager import connection_manager, resource_limiter
from app.services.ai_tracing import AITracer, TraceContext

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """Central orchestrator for AI operations with Epic E2 components."""

    def __init__(self):
        self.client = AIClient()
        self.policy_engine = AIPolicyEngine()
        self.context_builder = AIContextBuilder()
        self.normalizer = AINormalizer()
        self.fallback_manager = AIFallbackManager()
        self.tracer = AITracer()
        self.metrics = AIMetricsCollector()
        # Epic E3 components
        self.language_processor = LanguageProcessor()
        self.hybrid_search = HybridSearchEngine()
        self.recommendations_engine = AIRecommendationsEngine()
        self.query_processor = AIQueryProcessor()
        # Performance optimization components
        self.cache_manager = cache_manager
        self.performance_monitor = performance_monitor
        self.connection_manager = connection_manager
        self.resource_limiter = resource_limiter
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the orchestrator and all components."""
        if self._initialized:
            return

        # Initialize policy engine with default configuration
        policy_config = {
            "policies": {
                "cost_optimization_enabled": True,
                "performance_optimization_enabled": True,
                "fallback_enabled": True,
            }
        }
        self.policy_engine.initialize(policy_config)

        # AI Client is already initialized in its constructor
        self._initialized = True
        logger.info("AI Orchestrator initialized with Epic E2 and E3 components")

    @cache_ai_operation(prefix="semantic_search", ttl=1800)  # Cache for 30 minutes
    async def semantic_search(
        self,
        query: str,
        parts: List[Dict[str, Any]],
        limit: int = 10,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using AI with Epic E2 components and performance optimizations.

        Args:
            query: Search query
            parts: List of parts to search through
            limit: Maximum number of results
            user_id: User identifier for rate limiting
            **kwargs: Additional search parameters

        Returns:
            List of search results
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping semantic search.")
            return []

        # Check resource limits
        if not await self.resource_limiter.acquire_request_slot():
            logger.warning("Resource limit exceeded. Request rejected.")
            return []

        # Start tracing
        with TraceContext(
            self.tracer,
            "semantic_search",
            user_id=user_id,
            query=query[:50],  # Truncate for logging
            parts_count=len(parts),
            limit=limit,
        ):
            start_time = time.time()
            provider_name = "unknown"

            try:
                # Optimize query for better performance
                query_optimization = self.performance_monitor.optimize_query(
                    query, TaskType.SEMANTIC_SEARCH)
                optimized_query = query_optimization.get("optimized_query", query)

                if query_optimization.get("optimizations_applied"):
                    logger.debug(f"Query optimized: {query_optimization['optimizations_applied']}")

                # Build and sanitize context
                raw_context = {
                    "query": optimized_query,
                    "parts": parts,
                }
                self.context_builder.build_prompt(TaskType.SEMANTIC_SEARCH, raw_context)

                # Use policy engine to select best provider
                selected_provider = self.policy_engine.select_provider(
                    TaskType.SEMANTIC_SEARCH, self.client.providers, raw_context, user_id
                )

                # Execute with fallback manager
                response = await self.fallback_manager.execute_with_fallback(
                    self.client.providers,
                    selected_provider.name if selected_provider else self.client.primary_provider,
                    self.client.fallback_providers,
                    TaskType.SEMANTIC_SEARCH,
                    raw_context,
                    limit=limit,
                )

                provider_name = response.provider if response else "unknown"

                # Normalize response
                if response and response.content is not None:
                    response = self.normalizer.normalize_response(
                        response, TaskType.SEMANTIC_SEARCH)

                    # Record performance metrics
                    duration_ms = (time.time() - start_time) * 1000
                    self.performance_monitor.record_request(
                        provider_name=provider_name,
                        response_time=duration_ms / 1000,
                        success=True,
                        cost=response.cost,
                        tokens_used=response.metadata.get("tokens_used", 0),
                    )

                    # Record resource usage
                    await self.resource_limiter.record_request(
                        tokens_used=response.metadata.get("tokens_used", 0),
                        actual_cost=response.cost or 0.0,
                    )

                    # Record metrics
                    self.metrics.record_request(
                        provider=provider_name,
                        task_type=TaskType.SEMANTIC_SEARCH.value,
                        duration_ms=duration_ms,
                        success=True,
                        tokens_used=response.metadata.get("tokens_used", {}),
                        cost=response.cost,
                    )

                    logger.info(
                        f"Semantic search completed successfully. Found {len(response.content)} results.")
                    return response.content
                else:
                    # Record failure metrics
                    duration_ms = (time.time() - start_time) * 1000
                    self.performance_monitor.record_request(
                        provider_name=provider_name,
                        response_time=duration_ms / 1000,
                        success=False,
                        error_type="empty_response",
                    )

                    self.metrics.record_request(
                        provider=provider_name,
                        task_type=TaskType.SEMANTIC_SEARCH.value,
                        duration_ms=duration_ms,
                        success=False,
                        error_type="empty_response",
                    )

                    logger.warning(
                        f"Semantic search failed: {response.metadata.get('error', 'Unknown error') if response else 'No response'}")
                    return []

            except Exception as e:
                # Record error metrics
                duration_ms = (time.time() - start_time) * 1000
                self.performance_monitor.record_request(
                    provider_name=provider_name,
                    response_time=duration_ms / 1000,
                    success=False,
                    error_type=type(e).__name__,
                )

                self.metrics.record_request(
                    provider=provider_name,
                    task_type=TaskType.SEMANTIC_SEARCH.value,
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                )

                logger.error(f"Error in semantic search: {e}")
                return []
            finally:
                # Always release the request slot
                await self.resource_limiter.release_request_slot()

    async def intelligent_search(
        self,
        query: str,
        parts: List[Dict[str, Any]] = None,
        limit: int = 10,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Perform intelligent search with query understanding.

        Args:
            query: Search query
            parts: List of parts to search through
            limit: Maximum number of results
            user_id: User identifier for rate limiting
            **kwargs: Additional search parameters

        Returns:
            Dictionary containing search results and analysis
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping intelligent search.")
            return {
                "success": False,
                "parts": [],
                "query_analysis": None,
                "suggestions": [],
                "search_type": "basic",
                "error": "AI Gateway disabled",
            }

        logger.info(f"Orchestrating intelligent search for query: '{query}'")

        try:
            context = {
                "query": query,
                "parts": parts or [],
            }

            response = await self.client.execute_task(TaskType.INTELLIGENT_SEARCH, context, limit=limit)

            if response.content is not None:
                result = response.content
                logger.info("Intelligent search completed successfully.")
                return result
            else:
                logger.warning(
                    f"Intelligent search failed: {response.metadata.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "parts": [],
                    "query_analysis": None,
                    "suggestions": [],
                    "search_type": "basic",
                    "error": response.metadata.get("error", "Unknown error"),
                }

        except Exception as e:
            logger.error(f"Error in intelligent search: {e}")
            return {
                "success": False,
                "parts": [],
                "query_analysis": None,
                "suggestions": [],
                "search_type": "basic",
                "error": str(e),
            }

    async def get_part_recommendations(
        self,
        part_id: int,
        part_data: Dict[str, Any],
        limit: int = 5,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        Get AI-powered part recommendations.

        Args:
            part_id: ID of the reference part
            part_data: Data about the reference part
            limit: Maximum number of recommendations
            user_id: User identifier for rate limiting
            **kwargs: Additional recommendation parameters

        Returns:
            List of recommended parts
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping recommendations.")
            return []

        logger.info(f"Orchestrating recommendations for part ID: {part_id}")

        try:
            context = {
                "part_id": part_id,
                "part_data": part_data,
            }

            response = await self.client.execute_task(TaskType.PART_RECOMMENDATIONS, context, limit=limit)

            if response.content is not None:
                logger.info(
                    f"Part recommendations completed successfully. Generated {len(response.content)} recommendations."
                )
                return response.content
            else:
                logger.warning(
                    f"Part recommendations failed: {
                        response.metadata.get(
                            'error', 'Unknown error')}")
                return []

        except Exception as e:
            logger.error(f"Error in part recommendations: {e}")
            return []

    async def analyze_query(self,
                            query: str,
                            user_id: Optional[str] = None,
                            **kwargs) -> Dict[str,
                                              Any]:
        """
        Analyze user query to extract intent and entities.

        Args:
            query: Query to analyze
            user_id: User identifier for rate limiting
            **kwargs: Additional analysis parameters

        Returns:
            Query analysis results
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping query analysis.")
            return {"intent": "search", "entities": [], "language": "unknown"}

        logger.info(f"Orchestrating query analysis for: '{query}'")

        try:
            context = {
                "query": query,
            }

            response = await self.client.execute_task(TaskType.QUERY_ANALYSIS, context)

            if response.content is not None:
                logger.info("Query analysis completed successfully.")
                return response.content
            else:
                logger.warning(
                    f"Query analysis failed: {
                        response.metadata.get(
                            'error', 'Unknown error')}")
                return {"intent": "search", "entities": [], "language": "unknown"}

        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return {"intent": "search", "entities": [], "language": "unknown"}

    async def generate_suggestions(
        self,
        query: str,
        analysis: Dict[str, Any],
        results: List[Dict[str, Any]],
        limit: int = 3,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        Generate smart suggestions based on context.

        Args:
            query: Original search query
            analysis: Query analysis results
            results: Search results
            limit: Maximum number of suggestions
            user_id: User identifier for rate limiting
            **kwargs: Additional suggestion parameters

        Returns:
            List of generated suggestions
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping suggestion generation.")
            return []

        logger.info(f"Orchestrating suggestion generation for query: '{query}'")

        try:
            context = {
                "query": query,
                "analysis": analysis,
                "results": results,
            }

            response = await self.client.execute_task(TaskType.SUGGESTION_GENERATION, context)

            if response.content is not None:
                logger.info(
                    f"Suggestion generation completed successfully. Generated {len(response.content)} suggestions."
                )
                return response.content
            else:
                logger.warning(
                    f"Suggestion generation failed: {
                        response.metadata.get(
                            'error', 'Unknown error')}")
                return []

        except Exception as e:
            logger.error(f"Error in suggestion generation: {e}")
            return []

    def get_ai_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of AI Gateway and all components.
        """
        return {
            "enabled": getattr(settings, "ai_gateway_enabled", False),
            "experimental": getattr(settings, "ai_gateway_experimental", False),
            "providers": self.client.get_provider_status(),
            "policy_engine": {
                "initialized": self.policy_engine._initialized,
                "policies_count": len(self.policy_engine.policies),
            },
            "context_builder": {"token_budget": self.context_builder.token_budget},
            "normalizer": {"templates_count": len(self.normalizer.response_templates)},
            "fallback_manager": {
                "strategies_count": len(self.fallback_manager.fallback_strategies),
                "cache_stats": self.fallback_manager.get_cache_stats(),
            },
            "tracing": {
                "active_traces": len(self.tracer.active_traces),
                "completed_traces": len(self.tracer.completed_traces),
                "statistics": self.tracer.get_trace_statistics(),
            },
            "metrics": {
                "collection_period_hours": (time.time() - self.metrics.start_time.timestamp()) / 3600,
                "total_requests": sum(m.request_count for m in self.metrics.metrics.values()),
                "health_status": self.metrics.get_health_status(),
            },
            "performance": self.performance_monitor.get_performance_stats(),
            "caching": self.cache_manager.get_stats(),
            "resource_limits": self.resource_limiter.get_usage_stats(),
            "connection_pools": self.connection_manager.get_pool_stats(),
        }

    async def get_performance_health(self) -> Dict[str, Any]:
        """
        Get detailed performance health information.
        """
        return {
            "cache_health": await self.cache_manager.health_check(),
            "performance_stats": self.performance_monitor.get_performance_stats(),
            "resource_usage": self.resource_limiter.get_usage_stats(),
            "connection_pools": self.connection_manager.get_pool_stats(),
            "ai_gateway_status": self.get_ai_status(),
        }

    async def optimize_performance(self) -> Dict[str, Any]:
        """
        Perform performance optimization tasks.
        """
        optimizations = []

        try:
            # Clean up expired cache entries
            expired_count = await self.cache_manager.cleanup_expired()
            if expired_count > 0:
                optimizations.append(f"Cleaned up {expired_count} expired cache entries")

            # Adjust performance monitor weights
            self.performance_monitor.load_balancer.adjust_weights()
            optimizations.append("Adjusted provider weights based on performance")

            # Reset performance metrics if they're too old
            if hasattr(self.performance_monitor.global_metrics, "start_time"):
                uptime_hours = (
                    time.time() - self.performance_monitor.global_metrics.start_time) / 3600
                if uptime_hours > 24:  # Reset metrics daily
                    self.performance_monitor.reset_metrics()
                    optimizations.append("Reset performance metrics")

            return {
                "success": True,
                "optimizations_applied": optimizations,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {"success": False, "error": str(e), "timestamp": time.time()}
