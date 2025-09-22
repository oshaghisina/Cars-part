"""
AI Fallback Manager - Intelligent Fallback Strategies

This module manages fallback strategies when primary AI providers fail,
implementing intelligent retry logic and graceful degradation.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.services.ai_provider import AIProvider, AIResponse, TaskType

logger = logging.getLogger(__name__)


class AIFallbackManager:
    """
    Manages fallback strategies for AI provider failures.
    """

    def __init__(self):
        self.fallback_strategies = {
            "immediate": self._immediate_fallback,
            "delayed": self._delayed_fallback,
            "cached": self._cached_fallback,
            "simplified": self._simplified_fallback,
            "graceful_degradation": self._graceful_degradation_fallback,
        }
        self.failure_history: Dict[str, List[Dict[str, Any]]] = {}
        self.cache: Dict[str, Tuple[AIResponse, float]] = {}  # response, timestamp
        self.cache_ttl = getattr(settings, "ai_gateway_cache_ttl", 300)  # 5 minutes

    async def execute_with_fallback(
        self,
        providers: Dict[str, AIProvider],
        primary_provider: str,
        fallback_providers: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> AIResponse:
        """
        Execute a task with intelligent fallback strategies.

        Args:
            providers: Available AI providers
            primary_provider: Primary provider name
            fallback_providers: List of fallback provider names
            task_type: Type of AI task
            context: Context data for the task
            **kwargs: Additional task parameters

        Returns:
            AI response from successful provider or fallback
        """
        provider_chain = [primary_provider] + fallback_providers

        for strategy_name, strategy_func in self.fallback_strategies.items():
            logger.info(f"Attempting fallback strategy: {strategy_name}")

            try:
                result = await strategy_func(providers, provider_chain, task_type, context, **kwargs)

                if result and result.content is not None:
                    logger.info(f"Fallback strategy '{strategy_name}' succeeded")
                    return result

            except Exception as e:
                logger.warning(f"Fallback strategy '{strategy_name}' failed: {e}")
                continue

        # If all strategies fail, return a graceful error response
        logger.error("All fallback strategies failed")
        return self._create_error_response(task_type, "All fallback strategies failed")

    async def _immediate_fallback(
        self,
        providers: Dict[str, AIProvider],
        provider_chain: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> Optional[AIResponse]:
        """Try each provider in the chain immediately."""
        for provider_name in provider_chain:
            if provider_name not in providers:
                continue

            provider = providers[provider_name]

            # Skip if provider is unhealthy
            if not provider.is_available():
                logger.debug(f"Skipping unhealthy provider: {provider_name}")
                continue

            # Skip if provider doesn't support the task
            if task_type not in provider.get_capabilities():
                logger.debug(f"Provider {provider_name} doesn't support {task_type.value}")
                continue

            try:
                logger.info(f"Trying immediate fallback with provider: {provider_name}")
                response = await provider.execute_task(task_type, context, **kwargs)

                if response and response.content is not None:
                    self._record_success(provider_name, task_type)
                    return response
                else:
                    self._record_failure(provider_name, task_type, "Empty response")

            except Exception as e:
                self._record_failure(provider_name, task_type, str(e))
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue

        return None

    async def _delayed_fallback(
        self,
        providers: Dict[str, AIProvider],
        provider_chain: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> Optional[AIResponse]:
        """Try providers with increasing delays between attempts."""
        for i, provider_name in enumerate(provider_chain):
            if provider_name not in providers:
                continue

            provider = providers[provider_name]

            if not provider.is_available():
                continue

            if task_type not in provider.get_capabilities():
                continue

            # Add delay based on attempt number (exponential backoff)
            if i > 0:
                delay = min(2**i, 10)  # Max 10 seconds
                logger.info(f"Delayed fallback: waiting {delay}s before trying {provider_name}")
                await asyncio.sleep(delay)

            try:
                logger.info(f"Trying delayed fallback with provider: {provider_name}")
                response = await provider.execute_task(task_type, context, **kwargs)

                if response and response.content is not None:
                    self._record_success(provider_name, task_type)
                    return response
                else:
                    self._record_failure(provider_name, task_type, "Empty response")

            except Exception as e:
                self._record_failure(provider_name, task_type, str(e))
                logger.warning(f"Provider {provider_name} failed in delayed fallback: {e}")
                continue

        return None

    async def _cached_fallback(
        self,
        providers: Dict[str, AIProvider],
        provider_chain: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> Optional[AIResponse]:
        """Try to use cached response if available."""
        cache_key = self._generate_cache_key(task_type, context)

        # Check cache
        if cache_key in self.cache:
            cached_response, timestamp = self.cache[cache_key]

            # Check if cache is still valid
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Using cached response for {task_type.value}")
                cached_response.metadata = cached_response.metadata or {}
                cached_response.metadata["from_cache"] = True
                cached_response.metadata["cache_age"] = time.time() - timestamp
                return cached_response
            else:
                # Remove expired cache entry
                del self.cache[cache_key]

        # Try providers and cache successful response
        for provider_name in provider_chain:
            if provider_name not in providers:
                continue

            provider = providers[provider_name]

            if not provider.is_available():
                continue

            if task_type not in provider.get_capabilities():
                continue

            try:
                logger.info(f"Trying cached fallback with provider: {provider_name}")
                response = await provider.execute_task(task_type, context, **kwargs)

                if response and response.content is not None:
                    # Cache the response
                    self.cache[cache_key] = (response, time.time())
                    self._record_success(provider_name, task_type)
                    return response
                else:
                    self._record_failure(provider_name, task_type, "Empty response")

            except Exception as e:
                self._record_failure(provider_name, task_type, str(e))
                logger.warning(f"Provider {provider_name} failed in cached fallback: {e}")
                continue

        return None

    async def _simplified_fallback(
        self,
        providers: Dict[str, AIProvider],
        provider_chain: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> Optional[AIResponse]:
        """Try providers with simplified context to reduce complexity."""
        # Simplify context for fallback attempts
        simplified_context = self._simplify_context(context, task_type)

        for provider_name in provider_chain:
            if provider_name not in providers:
                continue

            provider = providers[provider_name]

            if not provider.is_available():
                continue

            if task_type not in provider.get_capabilities():
                continue

            try:
                logger.info(f"Trying simplified fallback with provider: {provider_name}")
                response = await provider.execute_task(task_type, simplified_context, **kwargs)

                if response and response.content is not None:
                    self._record_success(provider_name, task_type)
                    return response
                else:
                    self._record_failure(provider_name, task_type, "Empty response")

            except Exception as e:
                self._record_failure(provider_name, task_type, str(e))
                logger.warning(f"Provider {provider_name} failed in simplified fallback: {e}")
                continue

        return None

    async def _graceful_degradation_fallback(
        self,
        providers: Dict[str, AIProvider],
        provider_chain: List[str],
        task_type: TaskType,
        context: Dict[str, Any],
        **kwargs,
    ) -> Optional[AIResponse]:
        """Provide degraded functionality when all providers fail."""
        logger.warning("Attempting graceful degradation fallback")

        # Create a basic response based on task type
        if task_type == TaskType.SEMANTIC_SEARCH:
            return self._create_basic_search_response(context)
        elif task_type == TaskType.INTELLIGENT_SEARCH:
            return self._create_basic_intelligent_search_response(context)
        elif task_type == TaskType.QUERY_ANALYSIS:
            return self._create_basic_query_analysis_response(context)
        elif task_type == TaskType.SUGGESTION_GENERATION:
            return self._create_basic_suggestions_response(context)
        elif task_type == TaskType.PART_RECOMMENDATIONS:
            return self._create_basic_recommendations_response(context)
        else:
            return self._create_error_response(task_type, "Graceful degradation not implemented for this task type")

    def _generate_cache_key(self, task_type: TaskType, context: Dict[str, Any]) -> str:
        """Generate a cache key for the task and context."""
        # Create a simple hash of the task type and key context elements
        key_elements = [
            task_type.value,
            context.get("query", ""),
            str(context.get("parts", [])[:5]),  # First 5 parts only
            str(context.get("part_id", "")),
        ]
        return str(hash("|".join(key_elements)))

    def _simplify_context(self, context: Dict[str, Any], task_type: TaskType) -> Dict[str, Any]:
        """Simplify context to reduce complexity for fallback attempts."""
        simplified = {"query": context.get("query", "")}

        # Add minimal required fields based on task type
        if task_type == TaskType.SEMANTIC_SEARCH:
            # Limit parts to first 10 for semantic search
            parts = context.get("parts", [])
            simplified["parts"] = parts[:10] if isinstance(parts, list) else []

        elif task_type == TaskType.PART_RECOMMENDATIONS:
            simplified["part_id"] = context.get("part_id")
            simplified["part_data"] = context.get("part_data", {})

        return simplified

    def _record_success(self, provider_name: str, task_type: TaskType):
        """Record a successful operation."""
        if provider_name not in self.failure_history:
            self.failure_history[provider_name] = []

        self.failure_history[provider_name].append(
            {"timestamp": time.time(), "task_type": task_type.value, "success": True, "error": None}
        )

    def _record_failure(self, provider_name: str, task_type: TaskType, error: str):
        """Record a failed operation."""
        if provider_name not in self.failure_history:
            self.failure_history[provider_name] = []

        self.failure_history[provider_name].append(
            {
                "timestamp": time.time(),
                "task_type": task_type.value,
                "success": False,
                "error": error,
            }
        )

    def get_provider_reliability(self, provider_name: str) -> Dict[str, Any]:
        """Get reliability metrics for a provider."""
        if provider_name not in self.failure_history:
            return {"reliability": 1.0, "total_attempts": 0, "success_rate": 1.0}

        history = self.failure_history[provider_name]
        total_attempts = len(history)
        successful_attempts = sum(1 for entry in history if entry["success"])

        reliability = successful_attempts / total_attempts if total_attempts > 0 else 1.0

        return {
            "reliability": reliability,
            "total_attempts": total_attempts,
            "success_rate": reliability,
            "recent_failures": len([entry for entry in history[-10:] if not entry["success"]]),
        }

    def _create_error_response(self, task_type: TaskType, error_message: str) -> AIResponse:
        """Create a standardized error response."""
        return AIResponse(
            content=None,
            metadata={
                "error": error_message,
                "task_type": task_type.value,
                "fallback_used": True,
                "timestamp": time.time(),
            },
            provider="fallback_manager",
            task_type=task_type,
        )

    def _create_basic_search_response(self, context: Dict[str, Any]) -> AIResponse:
        """Create a basic search response when all providers fail."""
        query = context.get("query", "")
        parts = context.get("parts", [])

        # Simple text matching fallback
        results = []
        if isinstance(parts, list) and query:
            query_lower = query.lower()
            for part in parts[:5]:  # Limit to 5 results
                if isinstance(part, dict):
                    part_name = str(part.get("part_name", "")).lower()
                    if any(word in part_name for word in query_lower.split()):
                        result = part.copy()
                        result["search_score"] = 0.3
                        result["match_type"] = "basic_text"
                        result["matched_field"] = "fallback_search"
                        results.append(result)

        return AIResponse(
            content=results,
            metadata={
                "fallback_used": True,
                "fallback_type": "basic_text_search",
                "total_results": len(results),
            },
            provider="fallback_manager",
            task_type=TaskType.SEMANTIC_SEARCH,
        )

    def _create_basic_intelligent_search_response(self, context: Dict[str, Any]) -> AIResponse:
        """Create a basic intelligent search response."""
        return AIResponse(
            content={
                "success": True,
                "parts": [],
                "query_analysis": {"intent": "search", "language": "unknown", "entities": []},
                "suggestions": [],
                "search_type": "basic_fallback",
            },
            metadata={"fallback_used": True, "fallback_type": "basic_intelligent_search"},
            provider="fallback_manager",
            task_type=TaskType.INTELLIGENT_SEARCH,
        )

    def _create_basic_query_analysis_response(self, context: Dict[str, Any]) -> AIResponse:
        """Create a basic query analysis response."""
        query = context.get("query", "")

        return AIResponse(
            content={"intent": "search", "language": "unknown", "entities": [], "confidence": 0.5},
            metadata={
                "fallback_used": True,
                "fallback_type": "basic_query_analysis",
                "original_query": query,
            },
            provider="fallback_manager",
            task_type=TaskType.QUERY_ANALYSIS,
        )

    def _create_basic_suggestions_response(self, context: Dict[str, Any]) -> AIResponse:
        """Create basic suggestions response."""
        return AIResponse(
            content=[
                "Try searching with different keywords",
                "Check related car parts categories",
                "Contact support for assistance",
            ],
            metadata={"fallback_used": True, "fallback_type": "basic_suggestions"},
            provider="fallback_manager",
            task_type=TaskType.SUGGESTION_GENERATION,
        )

    def _create_basic_recommendations_response(self, context: Dict[str, Any]) -> AIResponse:
        """Create basic recommendations response."""
        return AIResponse(
            content=[
                {"part_name": "Related maintenance parts", "reason": "General recommendation"},
                {"part_name": "Alternative brands", "reason": "General recommendation"},
                {"part_name": "Compatible accessories", "reason": "General recommendation"},
            ],
            metadata={"fallback_used": True, "fallback_type": "basic_recommendations"},
            provider="fallback_manager",
            task_type=TaskType.PART_RECOMMENDATIONS,
        )

    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        logger.info("AI Fallback Manager cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        valid_entries = sum(1 for _, timestamp in self.cache.values() if current_time - timestamp < self.cache_ttl)

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "cache_ttl": self.cache_ttl,
        }
