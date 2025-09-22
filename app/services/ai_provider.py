"""
AI Provider Interface

This module defines the abstract base class for AI providers in the AI Gateway system.
It will be implemented in Epic E1 of the implementation plan.

Future implementation will include:
- Concrete provider implementations (OpenAI, Anthropic, Local)
- Provider health checks and capability detection
- Standardized request/response handling
- Error handling and retry logic
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class TaskType(Enum):
    """AI task types supported by providers."""
    SEMANTIC_SEARCH = "semantic_search"
    INTELLIGENT_SEARCH = "intelligent_search"
    QUERY_ANALYSIS = "query_analysis"
    SUGGESTION_GENERATION = "suggestion_generation"
    PART_RECOMMENDATIONS = "part_recommendations"


class AIResponse:
    """Standardized AI response format."""
    
    def __init__(self, 
                 content: Any,
                 metadata: Dict[str, Any],
                 provider: str,
                 task_type: TaskType,
                 cost: Optional[float] = None,
                 tokens_used: Optional[int] = None):
        self.content = content
        self.metadata = metadata
        self.provider = provider
        self.task_type = task_type
        self.cost = cost
        self.tokens_used = tokens_used


class ProviderStatus(Enum):
    """Status of AI provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self._status = ProviderStatus.UNKNOWN
        self._error_count = 0
        self._max_errors = config.get("max_errors", 5)
    
    @abstractmethod
    async def execute_task(self, 
                    task_type: TaskType, 
                    context: Dict[str, Any], 
                    **kwargs) -> AIResponse:
        """
        Execute an AI task.
        
        Args:
            task_type: Type of AI task to execute
            context: Context data for the task
            **kwargs: Additional task-specific parameters
            
        Returns:
            AIResponse: Standardized response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and healthy."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[TaskType]:
        """Get list of task types this provider supports."""
        pass
    
    @abstractmethod
    def estimate_cost(self, 
                     task_type: TaskType, 
                     context: Dict[str, Any]) -> float:
        """Estimate cost for a task before execution."""
        pass

    def is_healthy(self) -> bool:
        """Check if the provider is healthy."""
        return self._status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]

    def get_status(self) -> ProviderStatus:
        """Get the current status of the provider."""
        return self._status

    def _update_status(self, status: ProviderStatus):
        """Update the provider status."""
        if self._status != status:
            self._status = status

    def _handle_error(self, error: Exception):
        """Handle an error from the provider."""
        self._error_count += 1
        if self._error_count >= self._max_errors:
            self._update_status(ProviderStatus.UNHEALTHY)
        else:
            self._update_status(ProviderStatus.DEGRADED)

    def _handle_success(self):
        """Handle a successful operation."""
        if self._error_count > 0:
            self._error_count = max(0, self._error_count - 1)
        
        if self._error_count == 0:
            self._update_status(ProviderStatus.HEALTHY)
