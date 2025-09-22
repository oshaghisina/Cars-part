"""
AI Gateway Performance Monitoring and Optimization

This module provides comprehensive performance monitoring, optimization strategies,
and adaptive performance tuning for the AI Gateway.
"""

import logging
import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional

from app.services.ai_provider import TaskType

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Tracks performance metrics for AI operations."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics = {
            "response_times": deque(maxlen=window_size),
            "success_rates": deque(maxlen=window_size),
            "error_counts": defaultdict(int),
            "throughput": deque(maxlen=window_size),
            "cost_per_request": deque(maxlen=window_size),
            "token_usage": deque(maxlen=window_size),
        }
        self.start_time = time.time()
        self.total_requests = 0
        self.total_errors = 0

    def record_request(
        self,
        response_time: float,
        success: bool,
        error_type: Optional[str] = None,
        cost: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ):
        """Record a request's performance metrics."""
        self.total_requests += 1
        if not success:
            self.total_errors += 1
            if error_type:
                self.metrics["error_counts"][error_type] += 1

        self.metrics["response_times"].append(response_time)
        self.metrics["success_rates"].append(1 if success else 0)

        if cost is not None:
            self.metrics["cost_per_request"].append(cost)

        if tokens_used is not None:
            self.metrics["token_usage"].append(tokens_used)

    def get_average_response_time(self) -> float:
        """Get average response time."""
        if not self.metrics["response_times"]:
            return 0.0
        return sum(self.metrics["response_times"]) / len(self.metrics["response_times"])

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if not self.metrics["success_rates"]:
            return 0.0
        return (sum(self.metrics["success_rates"]) / len(self.metrics["success_rates"])) * 100

    def get_throughput(self, window_minutes: int = 5) -> float:
        """Get requests per minute."""
        if not self.metrics["response_times"]:
            return 0.0

        # Calculate requests in the last window_minutes
        time.time()
        window_minutes * 60

        # This is a simplified calculation - in practice, you'd track timestamps
        return len(self.metrics["response_times"]) / window_minutes

    def get_average_cost(self) -> float:
        """Get average cost per request."""
        if not self.metrics["cost_per_request"]:
            return 0.0
        return sum(self.metrics["cost_per_request"]) / len(self.metrics["cost_per_request"])

    def get_average_tokens(self) -> float:
        """Get average tokens per request."""
        if not self.metrics["token_usage"]:
            return 0.0
        return sum(self.metrics["token_usage"]) / len(self.metrics["token_usage"])

    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": self.get_error_rate(),
            "success_rate": self.get_success_rate(),
            "average_response_time": self.get_average_response_time(),
            "throughput_rpm": self.get_throughput(),
            "average_cost": self.get_average_cost(),
            "average_tokens": self.get_average_tokens(),
            "error_breakdown": dict(self.metrics["error_counts"]),
            "uptime_seconds": time.time() - self.start_time,
        }


class AdaptiveLoadBalancer:
    """Adaptive load balancer that adjusts based on performance metrics."""

    def __init__(self):
        self.provider_metrics: Dict[str, PerformanceMetrics] = {}
        self.provider_weights: Dict[str, float] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.last_adjustment = time.time()
        self.adjustment_interval = 60  # Adjust weights every 60 seconds

    def initialize_provider(self, provider_name: str):
        """Initialize metrics tracking for a provider."""
        self.provider_metrics[provider_name] = PerformanceMetrics()
        self.provider_weights[provider_name] = 1.0
        self.circuit_breakers[provider_name] = {
            "failures": 0,
            "last_failure": 0,
            "state": "closed",  # closed, open, half-open
            "threshold": 5,
            "timeout": 60,
        }

    def record_provider_request(
        self,
        provider_name: str,
        response_time: float,
        success: bool,
        error_type: Optional[str] = None,
        cost: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ):
        """Record a request for a specific provider."""
        if provider_name not in self.provider_metrics:
            self.initialize_provider(provider_name)

        self.provider_metrics[provider_name].record_request(response_time, success, error_type, cost, tokens_used)

        # Update circuit breaker
        if not success:
            self._update_circuit_breaker(provider_name, False)
        else:
            self._update_circuit_breaker(provider_name, True)

    def _update_circuit_breaker(self, provider_name: str, success: bool):
        """Update circuit breaker state for a provider."""
        cb = self.circuit_breakers[provider_name]
        current_time = time.time()

        if success:
            if cb["state"] == "half-open":
                cb["state"] = "closed"
                cb["failures"] = 0
        else:
            cb["failures"] += 1
            cb["last_failure"] = current_time

            if cb["failures"] >= cb["threshold"]:
                cb["state"] = "open"
                logger.warning(f"Circuit breaker opened for provider {provider_name}")

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available (circuit breaker not open)."""
        if provider_name not in self.circuit_breakers:
            return True

        cb = self.circuit_breakers[provider_name]
        current_time = time.time()

        if cb["state"] == "closed":
            return True
        elif cb["state"] == "open":
            # Check if timeout has passed
            if current_time - cb["last_failure"] > cb["timeout"]:
                cb["state"] = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def get_provider_weight(self, provider_name: str) -> float:
        """Get the current weight for a provider."""
        if not self.is_provider_available(provider_name):
            return 0.0

        if provider_name not in self.provider_weights:
            return 1.0

        return self.provider_weights[provider_name]

    def adjust_weights(self):
        """Adjust provider weights based on performance metrics."""
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_interval:
            return

        self.last_adjustment = current_time

        # Calculate performance scores for each provider
        scores = {}
        for provider_name, metrics in self.provider_metrics.items():
            if not self.is_provider_available(provider_name):
                scores[provider_name] = 0.0
                continue

            # Calculate composite score based on multiple factors
            response_time_score = max(0, 1 - (metrics.get_average_response_time() / 10.0))  # Normalize to 0-1
            success_rate_score = metrics.get_success_rate() / 100.0
            cost_score = max(0, 1 - (metrics.get_average_cost() * 100))  # Normalize cost

            # Weighted composite score
            composite_score = response_time_score * 0.4 + success_rate_score * 0.4 + cost_score * 0.2

            scores[provider_name] = composite_score

        # Normalize scores to weights
        total_score = sum(scores.values())
        if total_score > 0:
            for provider_name, score in scores.items():
                self.provider_weights[provider_name] = score / total_score
        else:
            # If all providers have zero score, use equal weights
            for provider_name in scores:
                self.provider_weights[provider_name] = 1.0 / len(scores)

        logger.info(f"Adjusted provider weights: {self.provider_weights}")

    def select_best_provider(self, available_providers: List[str]) -> Optional[str]:
        """Select the best provider based on current weights and availability."""
        if not available_providers:
            return None

        # Filter available providers
        available = [p for p in available_providers if self.is_provider_available(p)]
        if not available:
            return None

        # Select provider with highest weight
        best_provider = max(available, key=lambda p: self.get_provider_weight(p))
        return best_provider

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all providers."""
        stats = {}
        for provider_name, metrics in self.provider_metrics.items():
            cb = self.circuit_breakers.get(provider_name, {})
            stats[provider_name] = {
                "metrics": metrics.get_stats(),
                "weight": self.get_provider_weight(provider_name),
                "available": self.is_provider_available(provider_name),
                "circuit_breaker": {
                    "state": cb.get("state", "closed"),
                    "failures": cb.get("failures", 0),
                    "last_failure": cb.get("last_failure", 0),
                },
            }
        return stats


class QueryOptimizer:
    """Optimizes queries for better performance and cost efficiency."""

    def __init__(self):
        self.query_patterns = {}
        self.optimization_rules = self._initialize_optimization_rules()

    def _initialize_optimization_rules(self) -> Dict[str, Any]:
        """Initialize query optimization rules."""
        return {
            "max_query_length": 500,
            "min_query_length": 3,
            "persian_optimization": True,
            "english_optimization": True,
            "stop_words": {
                "persian": ["و", "در", "از", "به", "که", "این", "آن", "با", "برای"],
                "english": [
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                ],
            },
            "query_expansion": True,
            "semantic_boost": True,
        }

    def optimize_query(self, query: str, task_type: TaskType) -> Dict[str, Any]:
        """
        Optimize a query for better performance.

        Args:
            query: Original query
            task_type: Type of AI task

        Returns:
            Optimized query information
        """
        if not query or len(query.strip()) < self.optimization_rules["min_query_length"]:
            return {
                "original_query": query,
                "optimized_query": query,
                "optimizations_applied": [],
                "confidence": 0.0,
            }

        optimizations = []
        optimized_query = query.strip()

        # Length optimization
        if len(optimized_query) > self.optimization_rules["max_query_length"]:
            optimized_query = optimized_query[: self.optimization_rules["max_query_length"]]
            optimizations.append("truncated")

        # Language-specific optimizations
        if self._contains_persian(optimized_query):
            optimized_query = self._optimize_persian_query(optimized_query)
            optimizations.append("persian_optimized")
        elif self._contains_english(optimized_query):
            optimized_query = self._optimize_english_query(optimized_query)
            optimizations.append("english_optimized")

        # Stop word removal
        if self.optimization_rules["query_expansion"]:
            optimized_query = self._remove_stop_words(optimized_query)
            optimizations.append("stop_words_removed")

        # Calculate confidence based on optimizations applied
        confidence = min(1.0, len(optimizations) * 0.2 + 0.5)

        return {
            "original_query": query,
            "optimized_query": optimized_query,
            "optimizations_applied": optimizations,
            "confidence": confidence,
            "length_reduction": len(query) - len(optimized_query),
        }

    def _contains_persian(self, text: str) -> bool:
        """Check if text contains Persian characters."""
        persian_chars = set("\u0600-\u06FF")
        return any(char in persian_chars for char in text)

    def _contains_english(self, text: str) -> bool:
        """Check if text contains English characters."""
        english_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return any(char in english_chars for char in text)

    def _optimize_persian_query(self, query: str) -> str:
        """Apply Persian-specific optimizations."""
        # Remove extra spaces
        query = " ".join(query.split())

        # Normalize Persian characters
        persian_normalizations = {
            "ي": "ی",  # Arabic yeh to Persian yeh
            "ك": "ک",  # Arabic kaf to Persian kaf
            "ة": "ه",  # Arabic teh marbuta to Persian heh
        }

        for arabic, persian in persian_normalizations.items():
            query = query.replace(arabic, persian)

        return query

    def _optimize_english_query(self, query: str) -> str:
        """Apply English-specific optimizations."""
        # Convert to lowercase for consistency
        query = query.lower()

        # Remove extra spaces
        query = " ".join(query.split())

        return query

    def _remove_stop_words(self, query: str) -> str:
        """Remove stop words from query."""
        words = query.split()

        # Determine language and get appropriate stop words
        if self._contains_persian(query):
            stop_words = self.optimization_rules["stop_words"]["persian"]
        else:
            stop_words = self.optimization_rules["stop_words"]["english"]

        # Remove stop words
        filtered_words = [word for word in words if word.lower() not in stop_words]

        return " ".join(filtered_words) if filtered_words else query


class PerformanceMonitor:
    """Main performance monitoring and optimization coordinator."""

    def __init__(self):
        self.load_balancer = AdaptiveLoadBalancer()
        self.query_optimizer = QueryOptimizer()
        self.global_metrics = PerformanceMetrics()
        self.optimization_enabled = True
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def initialize_provider(self, provider_name: str):
        """Initialize monitoring for a provider."""
        self.load_balancer.initialize_provider(provider_name)

    def record_request(
        self,
        provider_name: str,
        response_time: float,
        success: bool,
        error_type: Optional[str] = None,
        cost: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ):
        """Record a request for performance tracking."""
        # Record for specific provider
        self.load_balancer.record_provider_request(provider_name, response_time, success, error_type, cost, tokens_used)

        # Record globally
        self.global_metrics.record_request(response_time, success, error_type, cost, tokens_used)

        # Adjust weights periodically
        self.load_balancer.adjust_weights()

        # Periodic cleanup
        self._periodic_cleanup()

    def optimize_query(self, query: str, task_type: TaskType) -> Dict[str, Any]:
        """Optimize a query for better performance."""
        return self.query_optimizer.optimize_query(query, task_type)

    def select_best_provider(self, available_providers: List[str]) -> Optional[str]:
        """Select the best provider based on performance metrics."""
        return self.load_balancer.select_best_provider(available_providers)

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available."""
        return self.load_balancer.is_provider_available(provider_name)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "global_metrics": self.global_metrics.get_stats(),
            "provider_stats": self.load_balancer.get_provider_stats(),
            "optimization_enabled": self.optimization_enabled,
            "query_optimizer_rules": self.query_optimizer.optimization_rules,
        }

    def _periodic_cleanup(self):
        """Perform periodic cleanup tasks."""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        self.last_cleanup = current_time

        # Clean up old metrics (keep only recent data)
        for metrics in self.load_balancer.provider_metrics.values():
            # This would be implemented based on your specific cleanup needs
            pass

        logger.debug("Performed periodic performance cleanup")

    def enable_optimization(self, enabled: bool = True):
        """Enable or disable performance optimizations."""
        self.optimization_enabled = enabled
        logger.info(f"Performance optimization {'enabled' if enabled else 'disabled'}")

    def reset_metrics(self):
        """Reset all performance metrics."""
        self.global_metrics = PerformanceMetrics()
        for provider_name in self.load_balancer.provider_metrics:
            self.load_balancer.initialize_provider(provider_name)
        logger.info("Performance metrics reset")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
