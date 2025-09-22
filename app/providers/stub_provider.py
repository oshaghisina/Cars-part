"""
Stub Provider - Mock Provider for Testing

This module provides a stub provider for testing and development purposes.
It will be implemented in Epic E8 of the implementation plan.

Future implementation will include:
- Predictable mock responses for testing
- Configurable response delays
- Error simulation capabilities
- Cost and token simulation
- Test scenario support
"""

from typing import Any, Dict, List

from app.services.ai_provider import AIProvider, AIResponse, TaskType


class StubProvider(AIProvider):
    """Stub provider for testing and development."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("stub", config)
        self.delay = config.get("delay", 0.1)
        self.error_rate = config.get("error_rate", 0.0)
        self.mock_responses = config.get("mock_responses", {})

    def execute_task(self, task_type: TaskType, context: Dict[str, Any], **kwargs) -> AIResponse:
        """
        Execute task with stub response.

        Args:
            task_type: Type of AI task to execute
            context: Context data for the task
            **kwargs: Additional task-specific parameters

        Returns:
            AIResponse: Mock response
        """
        # TODO: Implement in Epic E8
        # - Simulate processing delay
        # - Randomly simulate errors
        # - Return mock response
        # - Include realistic metadata
        raise NotImplementedError("Stub provider not implemented")

    def is_available(self) -> bool:
        """Stub provider is always available."""
        return True

    def get_capabilities(self) -> List[TaskType]:
        """Stub provider supports all task types."""
        return list(TaskType)

    def estimate_cost(self, task_type: TaskType, context: Dict[str, Any]) -> float:
        """Estimate mock cost."""
        # TODO: Implement in Epic E8
        # - Return realistic mock cost
        return 0.01

    def _generate_mock_response(
        self, task_type: TaskType, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mock response for task type."""
        # TODO: Implement in Epic E8
        # - Generate realistic mock data
        # - Vary based on task type
        # - Include proper structure
        return {}

    def _simulate_delay(self) -> None:
        """Simulate processing delay."""
        # TODO: Implement in Epic E8
        # - Add configurable delay
        # - Random jitter

    def _should_simulate_error(self) -> bool:
        """Determine if error should be simulated."""
        # TODO: Implement in Epic E8
        # - Use configured error rate
        # - Random error simulation
        return False
