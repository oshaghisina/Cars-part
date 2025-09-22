"""
AI Context Builder - Context Management and PII Redaction

This module provides context building capabilities for AI operations,
including PII redaction, token budgeting, and prompt construction.
"""

import logging
import re
from typing import Any, Dict

from app.services.ai_logging import PIIMasker
from app.services.ai_provider import TaskType

logger = logging.getLogger(__name__)


class AIContextBuilder:
    """
    Builds and manages context for AI operations with PII redaction and token budgeting.
    """

    def __init__(self, token_budget: int = 4000):
        self.token_budget = token_budget
        self.pii_masker = PIIMasker()
        self._initialize_prompt_templates()

    def _initialize_prompt_templates(self):
        """Initialize prompt templates for different task types."""
        self.prompt_templates = {
            TaskType.SEMANTIC_SEARCH: self._build_semantic_search_prompt,
            TaskType.INTELLIGENT_SEARCH: self._build_intelligent_search_prompt,
            TaskType.QUERY_ANALYSIS: self._build_query_analysis_prompt,
            TaskType.SUGGESTION_GENERATION: self._build_suggestion_prompt,
            TaskType.PART_RECOMMENDATIONS: self._build_recommendation_prompt,
        }

    def build_prompt(self, task_type: TaskType, context: Dict[str, Any]) -> str:
        """
        Build an optimized prompt for the given task type and context.

        Args:
            task_type: Type of AI task
            context: Context data

        Returns:
            Optimized prompt string
        """
        try:
            # Redact PII from context
            redacted_context = self._redact_context_pii(context)

            # Build task-specific prompt
            if task_type in self.prompt_templates:
                prompt = self.prompt_templates[task_type](redacted_context)
            else:
                prompt = self._build_generic_prompt(task_type, redacted_context)

            # Enforce token budget
            optimized_prompt = self.enforce_token_budget(prompt, self.token_budget)

            token_count = self._count_tokens(optimized_prompt)
            logger.debug(
                f"Built prompt for {task_type.value} with {token_count} tokens")
            return optimized_prompt

        except Exception as e:
            logger.error(f"Error building prompt for {task_type.value}: {e}")
            return self._build_fallback_prompt(task_type, context)

    def _redact_context_pii(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact PII from context data."""
        if isinstance(context, dict):
            return {key: self._redact_context_pii(value) for key, value in context.items()}
        elif isinstance(context, list):
            return [self._redact_context_pii(item) for item in context]
        elif isinstance(context, str):
            return self.pii_masker.mask_pii(context)
        else:
            return context

    def redact_pii(self, text: str) -> str:
        """
        Redact PII from text while preserving structure.

        Args:
            text: Text to redact

        Returns:
            Text with PII redacted
        """
        return self.pii_masker.mask_pii(text)

    def enforce_token_budget(self, text: str, max_tokens: int) -> str:
        """
        Enforce token budget by truncating or summarizing text.

        Args:
            text: Text to process
            max_tokens: Maximum token count

        Returns:
            Text within token budget
        """
        estimated_tokens = self._count_tokens(text)

        if estimated_tokens <= max_tokens:
            return text

        # If text is too long, truncate intelligently
        logger.warning(f"Text exceeds token budget ({estimated_tokens} > {max_tokens}), truncating")

        # Try to truncate at sentence boundaries
        sentences = re.split(r"[.!?]+", text)
        truncated_text = ""

        for sentence in sentences:
            test_text = truncated_text + sentence + ". "
            if self._count_tokens(test_text) <= max_tokens:
                truncated_text = test_text
            else:
                break

        # If still too long, truncate by characters
        if self._count_tokens(truncated_text) > max_tokens:
            # Rough estimation: 1 token ≈ 4 characters
            max_chars = max_tokens * 4
            truncated_text = text[:max_chars]

            # Try to end at word boundary
            last_space = truncated_text.rfind(" ")
            if last_space > max_chars * 0.9:  # If we're close to the limit
                truncated_text = truncated_text[:last_space]

        return truncated_text.strip()

    def _count_tokens(self, text: str) -> int:
        """
        Rough token counting (more sophisticated counting could be added).

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters for English
        # Persian text might have different tokenization
        if self._contains_persian(text):
            # Persian text might be more token-dense
            return len(text) // 3
        else:
            return len(text) // 4

    def _contains_persian(self, text: str) -> bool:
        """Check if text contains Persian characters."""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        return bool(persian_pattern.search(text))

    def summarize_context(self, context: Dict[str, Any], max_tokens: int) -> Dict[str, Any]:
        """
        Summarize context to fit within token budget.

        Args:
            context: Context to summarize
            max_tokens: Maximum token budget

        Returns:
            Summarized context
        """
        # Extract key information
        key_info = self.extract_key_information(str(context))

        # Build summary
        summary = {
            "query": context.get("query", ""),
            "task_type": str(context.get("task_type", "")),
            "key_entities": key_info.get("entities", []),
            "important_details": key_info.get("details", []),
            "truncated": True,
        }

        # Add essential fields
        for field in ["parts", "analysis", "results"]:
            if field in context:
                field_content = str(context[field])
                if self._count_tokens(field_content) > 100:  # If field is large
                    summary[field] = self.enforce_token_budget(field_content, 100)
                else:
                    summary[field] = context[field]

        return summary

    def extract_key_information(self, text: str) -> Dict[str, Any]:
        """
        Extract key information from text for context building.

        Args:
            text: Text to analyze

        Returns:
            Extracted key information
        """
        entities = []
        details = []

        # Extract car-related entities
        car_brands = re.findall(
            r"\b(Chery|JAC|Brilliance|BYD|Geely|Great Wall|MG)\b",
            text,
            re.IGNORECASE)
        entities.extend(car_brands)

        # Extract Persian car brands
        persian_brands = re.findall(r"\b(چری|جک|بریلیانس|بید|جیلی|گریت وال|ام جی)\b", text)
        entities.extend(persian_brands)

        # Extract part types
        part_types = re.findall(
            r"\b(brake|filter|engine|suspension|transmission|لنت|فیلتر|موتور|تعلیق|گیربکس)\b",
            text,
            re.IGNORECASE,
        )
        entities.extend(part_types)

        # Extract model numbers
        models = re.findall(r"\b(Tiggo \d+|X\d+|H\d+|Arizo \d+|تیگو \d+)\b", text, re.IGNORECASE)
        entities.extend(models)

        # Extract important details (numbers, years, etc.)
        numbers = re.findall(r"\b\d{4}\b", text)  # Years
        details.extend(numbers)

        # Extract prices
        prices = re.findall(r"\$\d+(?:\.\d{2})?|\d+ تومان", text)
        details.extend(prices)

        return {
            "entities": list(set(entities)),
            "details": list(set(details)),
            "text_length": len(text),
            "contains_persian": self._contains_persian(text),
        }

    def _build_semantic_search_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for semantic search."""
        query = context.get("query", "")
        parts = context.get("parts", [])

        prompt = f"""You are an AI assistant helping customers find car parts using semantic search.

Query: {query}

Available parts: {len(parts)} parts in database.

Instructions:
1. Find parts that are semantically similar to the query
2. Consider Persian and English terminology
3. Focus on car parts for Chinese vehicles (Chery, JAC, Brilliance, etc.)
4. Return relevant parts with similarity scores

Please provide semantic matches for: {query}"""

        return prompt

    def _build_intelligent_search_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for intelligent search."""
        query = context.get("query", "")

        prompt = f"""You are an AI assistant for a Chinese car parts business.

Query: {query}

Instructions:
1. Analyze the user's intent and extract key information
2. Identify the car brand, model, and part type
3. Detect the language (Persian/English)
4. Generate helpful suggestions for related parts
5. Provide search results in a structured format

Please analyze this query: {query}"""

        return prompt

    def _build_query_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for query analysis."""
        query = context.get("query", "")

        prompt = f"""Analyze this car parts search query and extract:

Query: {query}

Extract:
1. Intent (what the user wants to find)
2. Car brand/model mentioned
3. Part type/category
4. Language (Persian/English)
5. Specific requirements (front/rear, left/right, etc.)

Respond in JSON format with the extracted information."""

        return prompt

    def _build_suggestion_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for suggestion generation."""
        query = context.get("query", "")
        analysis = context.get("analysis", {})
        results = context.get("results", [])

        prompt = f"""Based on this car parts search, generate helpful suggestions:

Query: {query}
Analysis: {analysis}
Results found: {len(results)} parts

Generate 3 suggestions for:
1. Related parts the user might need
2. Alternative brands for the same part
3. Complementary parts for maintenance

Respond with just the suggestions, one per line."""

        return prompt

    def _build_recommendation_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for part recommendations."""
        part_data = context.get("part_data", {})

        prompt = f"""Based on this car part, generate recommendations:

Part: {part_data}

Generate 3-5 related car parts that customers might also need:
1. Complementary parts (parts that work together)
2. Alternative brands for the same part
3. Maintenance parts for the same vehicle

Return only the part names, one per line."""

        return prompt

    def _build_generic_prompt(self, task_type: TaskType, context: Dict[str, Any]) -> str:
        """Build a generic prompt for unknown task types."""
        return f"""You are an AI assistant helping with {task_type.value}.

Context: {context}

Please provide assistance based on the given context."""

    def _build_fallback_prompt(self, task_type: TaskType, context: Dict[str, Any]) -> str:
        """Build a fallback prompt when other methods fail."""
        return f"Please help with {task_type.value} for: {context.get('query', 'unknown query')}"
