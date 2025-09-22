"""
AI Metrics - Performance Monitoring and Metrics Collection

This module provides comprehensive metrics collection and monitoring for AI operations,
including performance metrics, cost tracking, and provider health monitoring.
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class PerformanceMetrics:
    """Performance metrics for AI operations."""

    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    cost_tracking: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AIMetricsCollector:
    """
    Collects and manages AI operation metrics.
    """

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.duration_samples: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.metric_points: List[MetricPoint] = []
        self.start_time = datetime.utcnow()

    def record_request(
        self,
        provider: str,
        task_type: str,
        duration_ms: float,
        success: bool,
        error_type: Optional[str] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        cost: Optional[float] = None,
        **tags,
    ):
        """
        Record a request metric.

        Args:
            provider: AI provider name
            task_type: Type of AI task
            duration_ms: Request duration in milliseconds
            success: Whether the request was successful
            error_type: Type of error if failed
            tokens_used: Token usage breakdown
            cost: Request cost
            **tags: Additional tags
        """
        key = f"{provider}:{task_type}"
        metrics = self.metrics[key]

        # Update counters
        metrics.request_count += 1
        if success:
            metrics.success_count += 1
        else:
            metrics.failure_count += 1
            if error_type:
                metrics.error_rates[error_type] = metrics.error_rates.get(error_type, 0) + 1

        # Update duration metrics
        metrics.total_duration_ms += duration_ms
        metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
        metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)
        metrics.avg_duration_ms = metrics.total_duration_ms / metrics.request_count

        # Store duration sample for percentile calculation
        self.duration_samples[key].append(duration_ms)

        # Update token usage
        if tokens_used:
            for token_type, count in tokens_used.items():
                metrics.token_usage[token_type] = metrics.token_usage.get(token_type, 0) + count

        # Update cost tracking
        if cost is not None:
            provider_cost_key = f"{provider}_cost"
            metrics.cost_tracking[provider_cost_key] = metrics.cost_tracking.get(
                provider_cost_key, 0.0) + cost

        metrics.last_updated = datetime.utcnow()

        # Add metric points
        self._add_metric_point(
            "ai_request_duration",
            duration_ms,
            {"provider": provider, "task_type": task_type, "success": str(success)},
            MetricType.HISTOGRAM,
        )

        if cost is not None:
            self._add_metric_point(
                "ai_request_cost",
                cost,
                {"provider": provider, "task_type": task_type},
                MetricType.COUNTER,
            )

    def record_provider_health(self, provider: str, status: str,
                               response_time_ms: Optional[float] = None):
        """Record provider health metrics."""
        self._add_metric_point(
            "ai_provider_health",
            1 if status == "healthy" else 0,
            {"provider": provider, "status": status},
            MetricType.GAUGE,
        )

        if response_time_ms is not None:
            self._add_metric_point(
                "ai_provider_response_time",
                response_time_ms,
                {"provider": provider},
                MetricType.HISTOGRAM,
            )

    def record_cache_metrics(self, operation: str, hit: bool, size: int):
        """Record cache-related metrics."""
        self._add_metric_point(
            "ai_cache_operation",
            1 if hit else 0,
            {"operation": operation, "hit": str(hit)},
            MetricType.COUNTER,
        )

        self._add_metric_point("ai_cache_size", size, {"operation": operation}, MetricType.GAUGE)

    def record_rate_limit(self, provider: str, limit_type: str, rate: float):
        """Record rate limiting metrics."""
        self._add_metric_point(
            "ai_rate_limit",
            rate,
            {"provider": provider, "limit_type": limit_type},
            MetricType.GAUGE,
        )

    def _add_metric_point(self, name: str, value: float,
                          tags: Dict[str, str], metric_type: MetricType):
        """Add a metric point."""
        metric_point = MetricPoint(
            name=name, value=value, timestamp=datetime.utcnow(), tags=tags, metric_type=metric_type
        )
        self.metric_points.append(metric_point)

        # Cleanup old metric points
        self._cleanup_old_metrics()

    def _cleanup_old_metrics(self):
        """Remove old metric points to prevent memory leaks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        self.metric_points = [mp for mp in self.metric_points if mp.timestamp > cutoff_time]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        summary = {
            "collection_period": {
                "start_time": self.start_time.isoformat(),
                "duration_hours": (datetime.utcnow() - self.start_time).total_seconds() / 3600,
                "retention_hours": self.retention_hours,
            },
            "total_requests": sum(m.request_count for m in self.metrics.values()),
            "total_successes": sum(m.success_count for m in self.metrics.values()),
            "total_failures": sum(m.failure_count for m in self.metrics.values()),
            "overall_success_rate": 0.0,
            "providers": {},
            "task_types": {},
            "cost_summary": {},
            "performance_summary": {},
        }

        # Calculate overall success rate
        total_requests = summary["total_requests"]
        if total_requests > 0:
            summary["overall_success_rate"] = summary["total_successes"] / total_requests

        # Aggregate by provider and task type
        provider_metrics = defaultdict(
            lambda: {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "total_cost": 0.0})
        task_type_metrics = defaultdict(
            lambda: {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "avg_duration": 0.0})

        for key, metrics in self.metrics.items():
            provider, task_type = key.split(":", 1)

            # Provider aggregation
            provider_metrics[provider]["requests"] += metrics.request_count
            provider_metrics[provider]["successes"] += metrics.success_count
            provider_metrics[provider]["failures"] += metrics.failure_count

            for cost_key, cost in metrics.cost_tracking.items():
                if cost_key.startswith(provider):
                    provider_metrics[provider]["total_cost"] += cost

            # Task type aggregation
            task_type_metrics[task_type]["requests"] += metrics.request_count
            task_type_metrics[task_type]["successes"] += metrics.success_count
            task_type_metrics[task_type]["failures"] += metrics.failure_count
            task_type_metrics[task_type]["avg_duration"] += metrics.avg_duration_ms

        # Calculate success rates and average durations
        for provider, data in provider_metrics.items():
            data["success_rate"] = data["successes"] / \
                data["requests"] if data["requests"] > 0 else 0.0

        for task_type, data in task_type_metrics.items():
            data["success_rate"] = data["successes"] / \
                data["requests"] if data["requests"] > 0 else 0.0
            data["avg_duration"] = data["avg_duration"] / \
                data["requests"] if data["requests"] > 0 else 0.0

        summary["providers"] = dict(provider_metrics)
        summary["task_types"] = dict(task_type_metrics)

        # Cost summary
        total_cost = sum(data["total_cost"] for data in provider_metrics.values())
        summary["cost_summary"] = {
            "total_cost": total_cost,
            "by_provider": {
                provider: data["total_cost"] for provider,
                data in provider_metrics.items()},
        }

        # Performance summary
        all_durations = []
        for metrics in self.metrics.values():
            all_durations.extend(self.duration_samples[f"{metrics.request_count}"])

        if all_durations:
            all_durations.sort()
            summary["performance_summary"] = {
                "avg_duration_ms": sum(all_durations) / len(all_durations),
                "min_duration_ms": min(all_durations),
                "max_duration_ms": max(all_durations),
                "p50_duration_ms": all_durations[len(all_durations) // 2],
                "p95_duration_ms": all_durations[int(len(all_durations) * 0.95)],
                "p99_duration_ms": all_durations[int(len(all_durations) * 0.99)],
            }

        return summary

    def get_provider_metrics(self, provider: str) -> Dict[str, Any]:
        """Get metrics for a specific provider."""
        provider_metrics = {}

        for key, metrics in self.metrics.items():
            if key.startswith(f"{provider}:"):
                task_type = key.split(":", 1)[1]
                provider_metrics[task_type] = {
                    "request_count": metrics.request_count,
                    "success_count": metrics.success_count,
                    "failure_count": metrics.failure_count,
                    "success_rate": metrics.success_count /
                    metrics.request_count if metrics.request_count > 0 else 0.0,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "min_duration_ms": metrics.min_duration_ms,
                    "max_duration_ms": metrics.max_duration_ms,
                    "token_usage": metrics.token_usage.copy(),
                    "cost_tracking": metrics.cost_tracking.copy(),
                    "error_rates": metrics.error_rates.copy(),
                    "last_updated": metrics.last_updated.isoformat(),
                }

        return provider_metrics

    def get_task_type_metrics(self, task_type: str) -> Dict[str, Any]:
        """Get metrics for a specific task type."""
        task_metrics = {}

        for key, metrics in self.metrics.items():
            if key.endswith(f":{task_type}"):
                provider = key.split(":", 1)[0]
                task_metrics[provider] = {
                    "request_count": metrics.request_count,
                    "success_count": metrics.success_count,
                    "failure_count": metrics.failure_count,
                    "success_rate": metrics.success_count /
                    metrics.request_count if metrics.request_count > 0 else 0.0,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "min_duration_ms": metrics.min_duration_ms,
                    "max_duration_ms": metrics.max_duration_ms,
                    "token_usage": metrics.token_usage.copy(),
                    "cost_tracking": metrics.cost_tracking.copy(),
                    "error_rates": metrics.error_rates.copy(),
                    "last_updated": metrics.last_updated.isoformat(),
                }

        return task_metrics

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of AI operations."""
        summary = self.get_metrics_summary()

        health_status = {
            "overall_health": "healthy",
            "issues": [],
            "recommendations": [],
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Check overall success rate
        if summary["overall_success_rate"] < 0.95:
            health_status["issues"].append(
                f"Low overall success rate: {summary['overall_success_rate']:.2%}")
            health_status["recommendations"].append(
                "Investigate provider failures and error patterns")

        # Check provider health
        for provider, data in summary["providers"].items():
            if data["success_rate"] < 0.9:
                health_status["issues"].append(
                    f"Provider '{provider}' has low success rate: {data['success_rate']:.2%}"
                )
                health_status["recommendations"].append(f"Check health of provider '{provider}'")

        # Check for high error rates
        total_errors = summary["total_failures"]
        if total_errors > 100:  # Arbitrary threshold
            health_status["issues"].append(f"High error count: {total_errors}")
            health_status["recommendations"].append("Review error logs and provider configurations")

        # Check performance
        if "performance_summary" in summary and summary["performance_summary"]:
            perf = summary["performance_summary"]
            if "avg_duration_ms" in perf and perf["avg_duration_ms"] > 5000:  # 5 seconds
                health_status["issues"].append(
                    f"Slow average response time: {perf['avg_duration_ms']:.0f}ms")
                health_status["recommendations"].append(
                    "Optimize provider configurations or consider fallbacks")

        # Check costs
        if "cost_summary" in summary:
            total_cost = summary["cost_summary"]["total_cost"]
            if total_cost > 100:  # $100 threshold
                health_status["issues"].append(f"High cost accumulation: ${total_cost:.2f}")
                health_status["recommendations"].append("Review cost optimization strategies")

        # Determine overall health
        if health_status["issues"]:
            health_status["overall_health"] = "degraded" if len(
                health_status["issues"]) < 3 else "unhealthy"

        return health_status

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            import json

            summary = self.get_metrics_summary()
            return json.dumps(summary, indent=2, default=str)
        elif format == "prometheus":
            return self._export_prometheus_format()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        for key, metrics in self.metrics.items():
            provider, task_type = key.split(":", 1)

            # Request count
            lines.append(
                f'ai_requests_total{{provider="{provider}", task_type="{task_type}"}} {metrics.request_count}')

            # Success count
            lines.append(
                f'ai_successes_total{{provider="{provider}", task_type="{task_type}"}} {metrics.success_count}'
            )

            # Failure count
            lines.append(
                f'ai_failures_total{{provider="{provider}", task_type="{task_type}"}} {metrics.failure_count}')

            # Duration metrics
            lines.append(
                f'ai_duration_seconds{{provider="{provider}", task_type="{task_type}", quantile="0.5"}} {metrics.p50_duration_ms / 1000}'
            )
            lines.append(
                f'ai_duration_seconds{{provider="{provider}", task_type="{task_type}", quantile="0.95"}} {metrics.p95_duration_ms / 1000}'
            )
            lines.append(
                f'ai_duration_seconds{{provider="{provider}", task_type="{task_type}", quantile="0.99"}} {metrics.p99_duration_ms / 1000}'
            )

            # Cost metrics
            for cost_key, cost in metrics.cost_tracking.items():
                lines.append(
                    f'ai_cost_total{{provider="{provider}", task_type="{task_type}", cost_type="{cost_key}"}} {cost}'
                )

        return "\n".join(lines)

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.duration_samples.clear()
        self.metric_points.clear()
        self.start_time = datetime.utcnow()
        logger.info("AI metrics reset")


# Global metrics collector instance
ai_metrics = AIMetricsCollector()
