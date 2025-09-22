"""
AI Client - Unified Client for AI Providers

This module provides a unified client interface for communicating with AI providers.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.providers.openai_provider import OpenAIProvider
from app.services.ai_provider import AIProvider, AIResponse, TaskType

logger = logging.getLogger(__name__)


class AIClient:
    """Unified client for AI provider communication."""

    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self._circuit_breaker_threshold = getattr(
            settings, "ai_gateway_circuit_breaker_threshold", 5
        )
        self._circuit_breaker_timeout = getattr(settings, "ai_gateway_circuit_breaker_timeout", 60)
        self._circuit_breaker_state: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self.initialize()

    def initialize(self) -> None:
        """Initialize the AI client with available providers."""
        if self._initialized:
            return

        if not self._is_gateway_enabled():
            logger.info("AI Gateway is disabled. No AI providers initialized.")
            self._initialized = True
            return

        logger.info("AI Gateway is enabled. Initializing providers...")

        # Initialize OpenAI provider if configured
        if (
            hasattr(settings, "openai_api_key")
            and settings.openai_api_key
            and settings.openai_api_key != "CHANGEME_YOUR_OPENAI_API_KEY"
        ):
            try:
                openai_config = {
                    "api_key": settings.openai_api_key,
                    "default_model": settings.openai_model,
                    "embedding_model": settings.openai_embedding_model,
                    "max_tokens": settings.openai_max_tokens,
                    "temperature": settings.openai_temperature,
                    "timeout": settings.openai_timeout,
                    "max_retries": settings.openai_max_retries,
                    "requests_per_minute": settings.openai_requests_per_minute,
                    "tokens_per_minute": settings.openai_tokens_per_minute,
                }
                self.providers["openai"] = OpenAIProvider("openai", openai_config)
                if not self.primary_provider:
                    self.primary_provider = "openai"
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")

        # Initialize stub provider for experimental mode
        if getattr(settings, "ai_gateway_experimental", False):
            # Create a simple stub provider for experimental mode
            from app.services.ai_provider import AIProvider

            class SimpleStubProvider(AIProvider):
                def __init__(self, name: str, config: Dict[str, Any]):
                    super().__init__(name, config)

                async def execute_task(
                    self, task_type: TaskType, context: Dict[str, Any], **kwargs
                ) -> AIResponse:
                    return AIResponse(
                        content=[{"stub": "data"}],
                        metadata={"stub": True},
                        provider=self.name,
                        task_type=task_type,
                    )

                def is_available(self) -> bool:
                    return True

                def get_capabilities(self) -> List[TaskType]:
                    return list(TaskType)

                def estimate_cost(self, task_type: TaskType, context: Dict[str, Any]) -> float:
                    return 0.0

            self.providers["stub"] = SimpleStubProvider("stub", {})
            if not self.primary_provider:
                self.primary_provider = "stub"
            logger.info("Stub provider initialized for experimental mode")

        # Set up fallback chain
        if self.providers:
            # Use configured fallback providers if available
            if hasattr(settings, "ai_gateway_fallback_providers_list"):
                configured_fallbacks = settings.ai_gateway_fallback_providers_list
                self.fallback_providers = [p for p in configured_fallbacks if p in self.providers]
            else:
                # Fallback to automatic ordering
                provider_names = list(self.providers.keys())
                if len(provider_names) > 1:
                    self.fallback_providers = provider_names[1:]

            logger.info(f"Primary provider: {self.primary_provider}")
            logger.info(f"Fallback providers: {self.fallback_providers}")
        else:
            logger.warning("No valid AI providers configured or enabled.")

        self._initialized = True

    def add_provider(self, provider: AIProvider) -> None:
        """Add a provider to the client."""
        self.providers[provider.name] = provider
        if not self.primary_provider:
            self.primary_provider = provider.name
        else:
            self.fallback_providers.append(provider.name)
        logger.info(f"Added provider: {provider.name}")

    def remove_provider(self, provider_name: str) -> None:
        """Remove a provider from the client."""
        if provider_name in self.providers:
            del self.providers[provider_name]
            if self.primary_provider == provider_name:
                self.primary_provider = (
                    self.fallback_providers.pop(0) if self.fallback_providers else None
                )
            elif provider_name in self.fallback_providers:
                self.fallback_providers.remove(provider_name)
            logger.info(f"Removed provider: {provider_name}")

    async def execute_task(
        self,
        task_type: TaskType,
        context: Dict[str, Any],
        provider_preference: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """
        Execute a task using the best available provider.

        Args:
            task_type: Type of AI task to execute
            context: Context data for the task
            provider_preference: Preferred provider name
            **kwargs: Additional task-specific parameters

        Returns:
            AIResponse: Standardized response
        """
        if not self._is_gateway_enabled():
            return AIResponse(
                content=None,
                metadata={"error": "AI Gateway disabled"},
                provider="none",
                task_type=task_type,
            )

        # Determine which provider to use
        if provider_preference:
            providers_to_try = [provider_preference] + [
                p for p in self.fallback_providers if p != provider_preference
            ]
        else:
            providers_to_try = (
                [self.primary_provider] + self.fallback_providers if self.primary_provider else []
            )

        last_error = None

        for provider_name in providers_to_try:
            if not provider_name or provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]

            # Check circuit breaker
            if self._is_circuit_breaker_open(provider_name):
                logger.warning(f"Circuit breaker open for provider '{provider_name}', skipping")
                continue

            # Check if provider supports the task
            if task_type not in provider.get_capabilities():
                logger.warning(
                    f"Provider '{provider_name}' does not support task type '{task_type}'"
                )
                continue

            # Check if provider is healthy
            if not provider.is_available():
                logger.warning(f"Provider '{provider_name}' is not available")
                continue

            try:
                # Execute task with timeout
                logger.info(f"Executing {task_type.value} with provider '{provider_name}'")

                response = await asyncio.wait_for(
                    provider.execute_task(task_type, context, **kwargs),
                    timeout=getattr(settings, "ai_gateway_timeout", 30.0),
                )

                # Track success
                self._track_success(provider_name)

                # Add provider info to response
                response.provider = provider_name

                logger.info(f"Task completed successfully with provider '{provider_name}'")
                return response

            except asyncio.TimeoutError:
                error_msg = f"Timeout executing task with provider '{provider_name}'"
                logger.error(error_msg)
                self._track_failure(provider_name, error_msg)
                last_error = error_msg

            except Exception as e:
                error_msg = f"Error executing task with provider '{provider_name}': {e}"
                logger.error(error_msg)
                self._track_failure(provider_name, error_msg)
                last_error = error_msg

        # All providers failed
        logger.error(f"All providers failed for task type '{task_type}'")
        return AIResponse(
            content=None,
            metadata={"error": f"All providers failed. Last error: {last_error}"},
            provider="none",
            task_type=task_type,
        )

    def get_available_providers(self, task_type: TaskType) -> List[str]:
        """Get list of available providers for a task type."""
        available = []
        for name, provider in self.providers.items():
            if (
                provider.is_available()
                and task_type in provider.get_capabilities()
                and not self._is_circuit_breaker_open(name)
            ):
                available.append(name)
        return available

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all providers."""
        status = {}
        for name, provider in self.providers.items():
            circuit_state = self._circuit_breaker_state.get(
                name, {"failures": 0, "last_failure": 0, "state": "closed"}
            )

            status[name] = {
                "available": provider.is_available(),
                "healthy": provider.is_healthy(),
                "status": provider.get_status().value,
                "capabilities": [task.value for task in provider.get_capabilities()],
                "circuit_breaker": {
                    "state": circuit_state["state"],
                    "failures": circuit_state["failures"],
                    "last_failure": circuit_state["last_failure"],
                },
            }
        return status

    def _is_circuit_breaker_open(self, provider_name: str) -> bool:
        """Check if circuit breaker is open for a provider."""
        if provider_name not in self._circuit_breaker_state:
            return False

        state = self._circuit_breaker_state[provider_name]
        if state["failures"] < self._circuit_breaker_threshold:
            return False

        # Check if timeout has passed
        if time.time() - state["last_failure"] > self._circuit_breaker_timeout:
            # Reset circuit breaker
            self._circuit_breaker_state[provider_name] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed",
            }
            return False

        return True

    def _track_success(self, provider_name: str):
        """Track successful request for circuit breaker."""
        if provider_name not in self._circuit_breaker_state:
            self._circuit_breaker_state[provider_name] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed",
            }

        # Reset failure count on success
        self._circuit_breaker_state[provider_name]["failures"] = 0
        self._circuit_breaker_state[provider_name]["state"] = "closed"

    def _track_failure(self, provider_name: str, error: str):
        """Track failed request for circuit breaker."""
        if provider_name not in self._circuit_breaker_state:
            self._circuit_breaker_state[provider_name] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed",
            }

        self._circuit_breaker_state[provider_name]["failures"] += 1
        self._circuit_breaker_state[provider_name]["last_failure"] = time.time()

        if (
            self._circuit_breaker_state[provider_name]["failures"]
            >= self._circuit_breaker_threshold
        ):
            self._circuit_breaker_state[provider_name]["state"] = "open"
            logger.warning(
                f"Circuit breaker opened for provider '{provider_name}' "
                f"after {self._circuit_breaker_threshold} failures"
            )

    def _is_gateway_enabled(self) -> bool:
        """Check if AI Gateway is enabled via feature flag."""
        return getattr(settings, "ai_gateway_enabled", False)
