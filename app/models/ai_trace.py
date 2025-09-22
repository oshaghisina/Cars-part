"""
AI Trace Models

This module defines models for AI request tracing and debugging.
It will be implemented in Epic E6 of the implementation plan.

Future implementation will include:
- Request trace models with correlation IDs
- Provider interaction tracking
- Performance metrics and timing
- Error tracking and debugging info
- Audit trail for compliance
"""

from enum import Enum

from pydantic import BaseModel


class TraceStatus(str, Enum):
    """Status of a trace."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AITrace(BaseModel):
    """AI request trace model."""

    # TODO: Implement in Epic E6
    # request_id: str = Field(description="Unique request identifier")
    # user_id: Optional[str] = Field(default=None, description="User identifier")
    # task_type: str = Field(description="Type of AI task")
    # status: TraceStatus = Field(description="Trace status")
    # start_time: datetime = Field(description="Request start time")
    # end_time: Optional[datetime] = Field(default=None, description="Request end time")
    # provider: Optional[str] = Field(default=None, description="Provider used")
    # cost: Optional[float] = Field(default=None, description="Request cost")
    # tokens_used: Optional[int] = Field(default=None, description="Tokens used")


class ProviderInteraction(BaseModel):
    """Provider interaction within a trace."""

    # TODO: Implement in Epic E6
    # provider: str = Field(description="Provider name")
    # attempt: int = Field(description="Attempt number")
    # start_time: datetime = Field(description="Interaction start time")
    # end_time: Optional[datetime] = Field(default=None, description="Interaction end time")
    # success: bool = Field(description="Whether interaction succeeded")
    # error_message: Optional[str] = Field(default=None, description="Error message if failed")


class TraceMetrics(BaseModel):
    """Performance metrics for a trace."""

    # TODO: Implement in Epic E6
    # total_duration: float = Field(description="Total request duration in seconds")
    # gateway_overhead: float = Field(description="Gateway overhead in seconds")
    # provider_duration: float = Field(description="Provider response time in seconds")
    # fallback_used: bool = Field(description="Whether fallback was used")
    # retry_count: int = Field(description="Number of retries")


class TraceContext(BaseModel):
    """Context information for a trace."""

    # TODO: Implement in Epic E6
    # query: str = Field(description="Original query (may be masked)")
    # masked_query: str = Field(description="Query with PII masked")
    # user_agent: Optional[str] = Field(default=None, description="User agent")
    # ip_address: Optional[str] = Field(default=None, description="IP address")
    # headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
