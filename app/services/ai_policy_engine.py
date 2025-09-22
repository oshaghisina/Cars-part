"""
AI Policy Engine - Intelligent Routing and Decision Making

This module implements the AI Policy Engine, which is responsible for making
intelligent routing decisions for AI tasks based on various policies,
cost considerations, performance metrics, and provider health.
It will be implemented in Epic E2 of the implementation plan.
"""

import logging
from typing import Any, Dict, List, Optional

from app.services.ai_provider import AIProvider, TaskType, ProviderStatus

logger = logging.getLogger(__name__)


class AIPolicyEngine:
    """
    Manages policies for AI task routing and provider selection.
    """

    def __init__(self):
        self.policies: Dict[str, Any] = {}
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initializes the policy engine with configuration.
        
        Args:
            config: Configuration dictionary for policies.
        """
        self.policies = config.get("policies", {})
        self._initialized = True
        logger.info("AI Policy Engine initialized.")

    def select_provider(
        self,
        task_type: TaskType,
        providers: Dict[str, AIProvider],
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        provider_preference: Optional[str] = None,
    ) -> Optional[AIProvider]:
        """
        Selects the best AI provider based on policies, capabilities, and health.
        
        Args:
            task_type: The type of AI task to execute.
            providers: A dictionary of available AIProvider instances.
            context: The context data for the AI task.
            user_id: Optional user ID for user-specific policies.
            provider_preference: Optional preferred provider name.
        
        Returns:
            The selected AIProvider instance, or None if no suitable provider is found.
        """
        if not self._initialized:
            logger.warning("Policy Engine not initialized. Cannot select provider.")
            return None

        eligible_providers: List[AIProvider] = []

        # Filter by capability and basic health
        for name, provider in providers.items():
            if provider.is_available() and task_type in provider.get_capabilities():
                eligible_providers.append(provider)
            else:
                logger.debug(f"Provider '{name}' not eligible for '{task_type.value}' (available: {provider.is_available()}, capabilities: {provider.get_capabilities()})")

        if not eligible_providers:
            logger.warning(f"No eligible providers found for task type '{task_type.value}'.")
            return None

        # Apply provider preference if specified
        if provider_preference and provider_preference in providers:
            preferred_provider = providers[provider_preference]
            if preferred_provider in eligible_providers:
                logger.debug(f"Provider preference '{provider_preference}' applied.")
                return preferred_provider
            else:
                logger.warning(f"Preferred provider '{provider_preference}' not eligible for task '{task_type.value}'.")

        # Apply policies to rank providers
        ranked_providers = self._apply_policies(eligible_providers, task_type, context, user_id)

        if ranked_providers:
            selected = ranked_providers[0]
            logger.info(f"Selected provider '{selected.name}' for task '{task_type.value}' based on policies.")
            return selected
        else:
            logger.warning(f"No provider selected after applying policies for task '{task_type.value}'.")
            return None

    def _apply_policies(
        self,
        providers: List[AIProvider],
        task_type: TaskType,
        context: Dict[str, Any],
        user_id: Optional[str],
    ) -> List[AIProvider]:
        """
        Applies a series of policies to rank eligible providers.
        """
        # Start with all eligible providers
        current_ranking = list(providers)

        # Apply policies in a defined order
        current_ranking = self._apply_capability_policy(current_ranking, task_type)
        current_ranking = self._apply_cost_policy(current_ranking, task_type, context)
        current_ranking = self._apply_performance_policy(current_ranking, task_type, context)
        current_ranking = self._apply_fallback_policy(current_ranking, task_type, context)
        # Add more policies as needed (e.g., security, compliance, user-specific)

        return current_ranking

    def _apply_cost_policy(
        self, providers: List[AIProvider], task_type: TaskType, context: Dict[str, Any]
    ) -> List[AIProvider]:
        """Prioritize providers based on estimated cost."""
        if not self.policies.get("cost_optimization_enabled", True):
            return providers

        # Estimate cost for each provider and sort by lowest cost
        providers_with_cost = []
        for provider in providers:
            try:
                cost = provider.estimate_cost(task_type, context)
                providers_with_cost.append((provider, cost))
            except Exception as e:
                logger.warning(f"Could not estimate cost for provider '{provider.name}': {e}")
                providers_with_cost.append((provider, float('inf'))) # Put providers with errors at the end

        providers_with_cost.sort(key=lambda x: x[1])
        logger.debug("Applied cost policy.")
        return [p for p, _ in providers_with_cost]

    def _apply_performance_policy(
        self, providers: List[AIProvider], task_type: TaskType, context: Dict[str, Any]
    ) -> List[AIProvider]:
        """Prioritize providers based on historical performance (e.g., latency, success rate)."""
        # This is a placeholder. Real implementation would involve metrics collection.
        # For now, we'll just keep the existing order or apply a simple heuristic.
        logger.debug("Applied performance policy (placeholder).")
        return providers

    def _apply_capability_policy(
        self, providers: List[AIProvider], task_type: TaskType
    ) -> List[AIProvider]:
        """Filter providers by explicit task capability (already done in select_provider, but can refine)."""
        # This step is mostly handled before, but could be used for more granular capability matching
        logger.debug("Applied capability policy.")
        return [p for p in providers if task_type in p.get_capabilities()]

    def _apply_fallback_policy(
        self, providers: List[AIProvider], task_type: TaskType, context: Dict[str, Any]
    ) -> List[AIProvider]:
        """Ensure fallback providers are considered if primary ones fail or are unhealthy."""
        # This policy ensures that if the primary provider is unhealthy or degraded,
        # healthy fallback providers are given preference.
        
        # Separate healthy from degraded/unhealthy
        healthy_providers = [p for p in providers if p.get_status() == ProviderStatus.HEALTHY]
        degraded_unhealthy_providers = [p for p in providers if p.get_status() in [ProviderStatus.DEGRADED, ProviderStatus.UNHEALTHY]]

        # Prioritize healthy providers
        if healthy_providers:
            logger.debug("Applied fallback policy: prioritizing healthy providers.")
            return healthy_providers + degraded_unhealthy_providers
        else:
            logger.debug("Applied fallback policy: no healthy providers, returning all.")
            return providers