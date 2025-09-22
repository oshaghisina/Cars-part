"""
AI Tracing - Request Correlation and Distributed Tracing

This module provides request correlation and tracing capabilities for AI operations,
enabling end-to-end visibility into AI request flows and performance.
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TraceStatus(Enum):
    """Status of a trace."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TraceSpan:
    """Represents a span in the trace."""
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.STARTED
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def finish(self, status: TraceStatus = TraceStatus.COMPLETED, error: Optional[str] = None):
        """Finish the span."""
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.status = status
        if error:
            self.error = error

    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value

    def add_log(self, message: str, level: str = "info", **kwargs):
        """Add a log entry to the span."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "level": level,
            **kwargs
        })


@dataclass
class Trace:
    """Represents a complete trace."""
    trace_id: str
    correlation_id: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.STARTED
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    spans: List[TraceSpan] = field(default_factory=list)
    tags: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, status: TraceStatus = TraceStatus.COMPLETED):
        """Finish the trace."""
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.status = status

    def add_span(self, span: TraceSpan):
        """Add a span to the trace."""
        self.spans.append(span)

    def add_tag(self, key: str, value: Any):
        """Add a tag to the trace."""
        self.tags[key] = value

    def get_span(self, span_id: str) -> Optional[TraceSpan]:
        """Get a span by ID."""
        for span in self.spans:
            if span.span_id == span_id:
                return span
        return None

    def get_root_spans(self) -> List[TraceSpan]:
        """Get root spans (spans without parent)."""
        return [span for span in self.spans if span.parent_span_id is None]

    def get_child_spans(self, parent_span_id: str) -> List[TraceSpan]:
        """Get child spans of a parent span."""
        return [span for span in self.spans if span.parent_span_id == parent_span_id]


class AITracer:
    """
    Provides distributed tracing for AI operations.
    """

    def __init__(self):
        self.active_traces: Dict[str, Trace] = {}
        self.completed_traces: Dict[str, Trace] = {}
        self.trace_retention_hours = 24
        self.max_active_traces = 1000

    def start_trace(
        self,
        operation_name: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **tags
    ) -> Trace:
        """
        Start a new trace.
        
        Args:
            operation_name: Name of the operation being traced
            correlation_id: Optional correlation ID for request tracking
            user_id: Optional user ID
            session_id: Optional session ID
            **tags: Additional tags for the trace
            
        Returns:
            Started trace
        """
        trace_id = str(uuid.uuid4())
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        trace = Trace(
            trace_id=trace_id,
            correlation_id=correlation_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id
        )
        
        # Add initial tags
        for key, value in tags.items():
            trace.add_tag(key, value)
        
        self.active_traces[trace_id] = trace
        
        # Cleanup old traces if we have too many
        if len(self.active_traces) > self.max_active_traces:
            self._cleanup_old_traces()
        
        logger.debug(f"Started trace {trace_id} for operation '{operation_name}'")
        return trace

    def start_span(
        self,
        trace_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        **tags
    ) -> TraceSpan:
        """
        Start a new span within a trace.
        
        Args:
            trace_id: ID of the parent trace
            operation_name: Name of the span operation
            parent_span_id: ID of the parent span (None for root spans)
            **tags: Additional tags for the span
            
        Returns:
            Started span
        """
        if trace_id not in self.active_traces:
            raise ValueError(f"Trace {trace_id} not found")
        
        span_id = str(uuid.uuid4())
        span = TraceSpan(
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow()
        )
        
        # Add initial tags
        for key, value in tags.items():
            span.add_tag(key, value)
        
        self.active_traces[trace_id].add_span(span)
        
        logger.debug(f"Started span {span_id} '{operation_name}' in trace {trace_id}")
        return span

    def finish_span(
        self,
        trace_id: str,
        span_id: str,
        status: TraceStatus = TraceStatus.COMPLETED,
        error: Optional[str] = None
    ):
        """
        Finish a span.
        
        Args:
            trace_id: ID of the parent trace
            span_id: ID of the span to finish
            status: Final status of the span
            error: Optional error message
        """
        if trace_id not in self.active_traces:
            logger.warning(f"Trace {trace_id} not found when finishing span {span_id}")
            return
        
        span = self.active_traces[trace_id].get_span(span_id)
        if not span:
            logger.warning(f"Span {span_id} not found in trace {trace_id}")
            return
        
        span.finish(status, error)
        logger.debug(f"Finished span {span_id} with status {status.value}")

    def finish_trace(
        self,
        trace_id: str,
        status: TraceStatus = TraceStatus.COMPLETED
    ):
        """
        Finish a trace.
        
        Args:
            trace_id: ID of the trace to finish
            status: Final status of the trace
        """
        if trace_id not in self.active_traces:
            logger.warning(f"Trace {trace_id} not found when finishing")
            return
        
        trace = self.active_traces[trace_id]
        trace.finish(status)
        
        # Move to completed traces
        self.completed_traces[trace_id] = trace
        del self.active_traces[trace_id]
        
        logger.info(f"Finished trace {trace_id} with status {status.value}")

    def add_trace_tag(self, trace_id: str, key: str, value: Any):
        """Add a tag to a trace."""
        if trace_id in self.active_traces:
            self.active_traces[trace_id].add_tag(key, value)
        elif trace_id in self.completed_traces:
            self.completed_traces[trace_id].add_tag(key, value)

    def add_span_tag(self, trace_id: str, span_id: str, key: str, value: Any):
        """Add a tag to a span."""
        if trace_id in self.active_traces:
            span = self.active_traces[trace_id].get_span(span_id)
            if span:
                span.add_tag(key, value)

    def add_span_log(
        self,
        trace_id: str,
        span_id: str,
        message: str,
        level: str = "info",
        **kwargs
    ):
        """Add a log entry to a span."""
        if trace_id in self.active_traces:
            span = self.active_traces[trace_id].get_span(span_id)
            if span:
                span.add_log(message, level, **kwargs)

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID."""
        if trace_id in self.active_traces:
            return self.active_traces[trace_id]
        elif trace_id in self.completed_traces:
            return self.completed_traces[trace_id]
        return None

    def get_traces_by_correlation_id(self, correlation_id: str) -> List[Trace]:
        """Get all traces with a specific correlation ID."""
        traces = []
        
        for trace in self.active_traces.values():
            if trace.correlation_id == correlation_id:
                traces.append(trace)
        
        for trace in self.completed_traces.values():
            if trace.correlation_id == correlation_id:
                traces.append(trace)
        
        return traces

    def get_traces_by_user(self, user_id: str) -> List[Trace]:
        """Get all traces for a specific user."""
        traces = []
        
        for trace in self.active_traces.values():
            if trace.user_id == user_id:
                traces.append(trace)
        
        for trace in self.completed_traces.values():
            if trace.user_id == user_id:
                traces.append(trace)
        
        return traces

    def _cleanup_old_traces(self):
        """Clean up old traces to prevent memory leaks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.trace_retention_hours)
        
        # Clean up completed traces
        traces_to_remove = []
        for trace_id, trace in self.completed_traces.items():
            if trace.start_time < cutoff_time:
                traces_to_remove.append(trace_id)
        
        for trace_id in traces_to_remove:
            del self.completed_traces[trace_id]
        
        # Clean up old active traces (shouldn't happen often)
        traces_to_remove = []
        for trace_id, trace in self.active_traces.items():
            if trace.start_time < cutoff_time:
                traces_to_remove.append(trace_id)
        
        for trace_id in traces_to_remove:
            logger.warning(f"Cleaning up old active trace {trace_id}")
            del self.active_traces[trace_id]
        
        if traces_to_remove:
            logger.info(f"Cleaned up {len(traces_to_remove)} old traces")

    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics about traces."""
        active_count = len(self.active_traces)
        completed_count = len(self.completed_traces)
        
        # Calculate average duration for completed traces
        total_duration = 0
        trace_count = 0
        status_counts = {}
        
        for trace in self.completed_traces.values():
            if trace.duration_ms is not None:
                total_duration += trace.duration_ms
                trace_count += 1
            
            status = trace.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_duration = total_duration / trace_count if trace_count > 0 else 0
        
        return {
            "active_traces": active_count,
            "completed_traces": completed_count,
            "total_traces": active_count + completed_count,
            "average_duration_ms": avg_duration,
            "status_distribution": status_counts,
            "retention_hours": self.trace_retention_hours
        }


class TraceContext:
    """
    Context manager for tracing operations.
    """

    def __init__(
        self,
        tracer: AITracer,
        operation_name: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **tags
    ):
        self.tracer = tracer
        self.operation_name = operation_name
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.tags = tags
        self.trace = None
        self.span = None

    def __enter__(self):
        """Start the trace."""
        self.trace = self.tracer.start_trace(
            self.operation_name,
            self.correlation_id,
            self.user_id,
            **self.tags
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish the trace."""
        if self.trace:
            status = TraceStatus.FAILED if exc_type else TraceStatus.COMPLETED
            error = str(exc_val) if exc_val else None
            self.tracer.finish_trace(self.trace.trace_id, status)
            
            if error:
                self.tracer.add_trace_tag(self.trace.trace_id, "error", error)

    def start_span(self, operation_name: str, **tags) -> 'SpanContext':
        """Start a span within this trace."""
        if not self.trace:
            raise ValueError("Trace not started")
        
        span = self.tracer.start_span(
            self.trace.trace_id,
            operation_name,
            **tags
        )
        
        return SpanContext(self.tracer, self.trace.trace_id, span)


class SpanContext:
    """
    Context manager for span operations.
    """

    def __init__(self, tracer: AITracer, trace_id: str, span: TraceSpan):
        self.tracer = tracer
        self.trace_id = trace_id
        self.span = span

    def __enter__(self):
        """Enter the span context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the span context."""
        status = TraceStatus.FAILED if exc_type else TraceStatus.COMPLETED
        error = str(exc_val) if exc_val else None
        self.tracer.finish_span(self.trace_id, self.span.span_id, status, error)

    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.span.add_tag(key, value)

    def add_log(self, message: str, level: str = "info", **kwargs):
        """Add a log entry to the span."""
        self.span.add_log(message, level, **kwargs)


# Global tracer instance
ai_tracer = AITracer()
