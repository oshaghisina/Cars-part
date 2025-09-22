"""
AI Configuration Models

This module defines Pydantic models for AI Gateway configuration and policies.
It will be implemented in Epic E2 of the implementation plan.

Future implementation will include:
- Policy configuration models
- Provider configuration schemas
- Rate limiting and budget models
- Feature flag models
- Validation and serialization
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PolicyType(str, Enum):
    """Types of AI policies."""
    RATE_LIMIT = "rate_limit"
    BUDGET_CONTROL = "budget_control"
    ROUTING_RULE = "routing_rule"
    CIRCUIT_BREAKER = "circuit_breaker"


class AIConfig(BaseModel):
    """Base AI configuration model."""
    # TODO: Implement in Epic E2
    pass


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    # TODO: Implement in Epic E2
    # per_user_rpm: int = Field(default=20, description="Requests per minute per user")
    # per_ip_rpm: int = Field(default=100, description="Requests per minute per IP")
    # burst_allowance: int = Field(default=50, description="Burst allowance percentage")
    pass


class BudgetConfig(BaseModel):
    """Budget control configuration."""
    # TODO: Implement in Epic E2
    # monthly_limit: float = Field(default=500.0, description="Monthly budget limit")
    # daily_limit: float = Field(default=20.0, description="Daily budget limit")
    # per_request_limit: float = Field(default=0.10, description="Per-request cost limit")
    pass


class ProviderConfig(BaseModel):
    """Provider configuration."""
    # TODO: Implement in Epic E2
    # name: str = Field(description="Provider name")
    # enabled: bool = Field(default=True, description="Whether provider is enabled")
    # weight: float = Field(default=1.0, description="Load balancing weight")
    # timeout: int = Field(default=5, description="Request timeout in seconds")
    # max_retries: int = Field(default=3, description="Maximum retry attempts")
    pass


class RoutingRule(BaseModel):
    """Routing rule configuration."""
    # TODO: Implement in Epic E2
    # task_type: str = Field(description="Task type this rule applies to")
    # provider_preference: List[str] = Field(description="Preferred providers in order")
    # fallback_enabled: bool = Field(default=True, description="Enable fallback")
    pass


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""
    # TODO: Implement in Epic E2
    # failure_threshold: int = Field(default=5, description="Failure threshold")
    # timeout: int = Field(default=30, description="Circuit breaker timeout")
    # recovery_timeout: int = Field(default=60, description="Recovery timeout")
    pass


class FeatureFlag(BaseModel):
    """Feature flag configuration."""
    # TODO: Implement in Epic E2
    # name: str = Field(description="Feature flag name")
    # enabled: bool = Field(default=False, description="Whether feature is enabled")
    # description: Optional[str] = Field(default=None, description="Feature description")
    pass
