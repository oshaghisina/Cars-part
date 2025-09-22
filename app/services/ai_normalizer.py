"""
AI Normalizer - Response Standardization and Formatting

This module provides response normalization capabilities for AI operations,
ensuring consistent output formats across different providers and task types.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.ai_provider import AIResponse, TaskType

logger = logging.getLogger(__name__)


class AINormalizer:
    """
    Normalizes AI responses to ensure consistent output formats across providers.
    """

    def __init__(self):
        self.response_templates = {
            TaskType.SEMANTIC_SEARCH: self._normalize_semantic_search_response,
            TaskType.INTELLIGENT_SEARCH: self._normalize_intelligent_search_response,
            TaskType.QUERY_ANALYSIS: self._normalize_query_analysis_response,
            TaskType.SUGGESTION_GENERATION: self._normalize_suggestion_response,
            TaskType.PART_RECOMMENDATIONS: self._normalize_recommendation_response,
        }

    def normalize_response(self, response: AIResponse, task_type: TaskType) -> AIResponse:
        """
        Normalize an AI response to ensure consistent format.

        Args:
            response: Raw AI response
            task_type: Type of task that generated the response

        Returns:
            Normalized AI response
        """
        try:
            if not response.content:
                return response

            # Apply task-specific normalization
            if task_type in self.response_templates:
                normalized_content = self.response_templates[task_type](response.content)
            else:
                normalized_content = self._normalize_generic_response(response.content)

            # Add metadata if missing
            if not response.metadata:
                response.metadata = {}

            response.metadata.update(
                {
                    "normalized": True,
                    "normalization_timestamp": datetime.utcnow().isoformat(),
                    "original_content_type": type(response.content).__name__,
                    "normalized_content_type": type(normalized_content).__name__,
                }
            )

            # Update the response content
            response.content = normalized_content

            logger.debug(f"Normalized {task_type.value} response from {response.provider}")
            return response

        except Exception as e:
            logger.error(f"Error normalizing {task_type.value} response: {e}")
            # Return original response with error metadata
            if not response.metadata:
                response.metadata = {}
            response.metadata.update({"normalization_error": str(e), "normalization_failed": True})
            return response

    def _normalize_semantic_search_response(self, content: Any) -> List[Dict[str, Any]]:
        """Normalize semantic search response."""
        if isinstance(content, list):
            normalized_results = []
            for item in content:
                if isinstance(item, dict):
                    normalized_item = {
                        "part_name": self._extract_part_name(item),
                        "brand_oem": self._extract_brand(item),
                        "vehicle_make": self._extract_vehicle_make(item),
                        "vehicle_model": self._extract_vehicle_model(item),
                        "category": self._extract_category(item),
                        "search_score": self._extract_search_score(item),
                        "match_type": self._extract_match_type(item),
                        "matched_field": self._extract_matched_field(item),
                        "price": self._extract_price(item),
                        "availability": self._extract_availability(item),
                        "description": self._extract_description(item),
                        "raw_data": item,  # Keep original for debugging
                    }
                    normalized_results.append(normalized_item)
                else:
                    # Convert non-dict items to standard format
                    normalized_results.append(
                        {
                            "part_name": str(item),
                            "search_score": 0.5,
                            "match_type": "unknown",
                            "matched_field": "raw_conversion",
                            "raw_data": item,
                        }
                    )
            return normalized_results
        else:
            # Single item response
            return [self._normalize_semantic_search_response([content])[0]]

    def _normalize_intelligent_search_response(self, content: Any) -> Dict[str, Any]:
        """Normalize intelligent search response."""
        if isinstance(content, dict):
            normalized = {
                "success": content.get("success", True),
                "parts": self._normalize_parts_list(content.get("parts", [])),
                "query_analysis": self._normalize_query_analysis(content.get("query_analysis", {})),
                "suggestions": self._normalize_suggestions(content.get("suggestions", [])),
                "search_type": content.get("search_type", "intelligent"),
                "total_results": len(content.get("parts", [])),
                "processing_time_ms": content.get("processing_time_ms"),
                "raw_response": content,
            }
            return normalized
        else:
            return {
                "success": False,
                "parts": [],
                "query_analysis": {},
                "suggestions": [],
                "search_type": "basic",
                "error": "Invalid response format",
                "raw_response": content,
            }

    def _normalize_query_analysis_response(self, content: Any) -> Dict[str, Any]:
        """Normalize query analysis response."""
        if isinstance(content, dict):
            return {
                "intent": content.get("intent", "search"),
                "car_brand": content.get("car_brand"),
                "car_model": content.get("car_model"),
                "part_type": content.get("part_type"),
                "language": content.get("language", "unknown"),
                "position": content.get("position"),
                "specific_requirements": content.get("specific_requirements", []),
                "confidence": content.get("confidence", 0.8),
                "entities": content.get("entities", []),
                "raw_analysis": content,
            }
        else:
            return {
                "intent": "search",
                "language": "unknown",
                "entities": [],
                "confidence": 0.0,
                "raw_analysis": content,
            }

    def _normalize_suggestion_response(self, content: Any) -> List[str]:
        """Normalize suggestion response."""
        if isinstance(content, list):
            return [str(item).strip() for item in content if item and str(item).strip()]
        elif isinstance(content, str):
            # Split by newlines and clean up
            suggestions = [line.strip() for line in content.split("\n") if line.strip()]
            return suggestions
        else:
            return [str(content).strip()] if content else []

    def _normalize_recommendation_response(self, content: Any) -> List[Dict[str, Any]]:
        """Normalize recommendation response."""
        if isinstance(content, list):
            normalized_recommendations = []
            for item in content:
                if isinstance(item, dict):
                    normalized_recommendations.append(
                        {
                            "part_name": item.get("part_name", str(item)),
                            "category": item.get("category"),
                            "brand": item.get("brand"),
                            "price_range": item.get("price_range"),
                            "compatibility": item.get("compatibility"),
                            "reason": item.get("reason", "Recommended"),
                            "confidence": item.get("confidence", 0.7),
                            "raw_recommendation": item,
                        }
                    )
                else:
                    normalized_recommendations.append(
                        {
                            "part_name": str(item),
                            "reason": "Recommended",
                            "confidence": 0.5,
                            "raw_recommendation": item,
                        }
                    )
            return normalized_recommendations
        else:
            return [
                {
                    "part_name": str(content),
                    "reason": "Recommended",
                    "confidence": 0.5,
                    "raw_recommendation": content,
                }
            ]

    def _normalize_generic_response(self, content: Any) -> Any:
        """Normalize generic response."""
        # For unknown response types, try to preserve structure but ensure it's serializable
        if isinstance(content, (str, int, float, bool, list, dict)):
            return content
        else:
            return str(content)

    def _normalize_parts_list(self, parts: List[Any]) -> List[Dict[str, Any]]:
        """Normalize a list of parts."""
        if not isinstance(parts, list):
            return []

        normalized_parts = []
        for part in parts:
            if isinstance(part, dict):
                normalized_parts.append(
                    {
                        "part_name": self._extract_part_name(part),
                        "brand_oem": self._extract_brand(part),
                        "vehicle_make": self._extract_vehicle_make(part),
                        "vehicle_model": self._extract_vehicle_model(part),
                        "category": self._extract_category(part),
                        "search_score": self._extract_search_score(part),
                        "match_type": self._extract_match_type(part),
                        "matched_field": self._extract_matched_field(part),
                        "price": self._extract_price(part),
                        "availability": self._extract_availability(part),
                        "description": self._extract_description(part),
                        "raw_data": part,
                    }
                )
            else:
                normalized_parts.append({"part_name": str(part), "raw_data": part})

        return normalized_parts

    def _normalize_query_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize query analysis data."""
        return {
            "intent": analysis.get("intent", "search"),
            "car_brand": analysis.get("car_brand"),
            "car_model": analysis.get("car_model"),
            "part_type": analysis.get("part_type"),
            "language": analysis.get("language", "unknown"),
            "position": analysis.get("position"),
            "specific_requirements": analysis.get("specific_requirements", []),
            "confidence": analysis.get("confidence", 0.8),
            "entities": analysis.get("entities", []),
        }

    def _normalize_suggestions(self, suggestions: List[Any]) -> List[str]:
        """Normalize suggestions list."""
        if not isinstance(suggestions, list):
            return []

        return [str(item).strip() for item in suggestions if item and str(item).strip()]

    # Helper methods for extracting specific fields
    def _extract_part_name(self, item: Dict[str, Any]) -> str:
        """Extract part name from item."""
        return item.get("part_name") or item.get("name") or item.get("title") or str(item.get("id", ""))

    def _extract_brand(self, item: Dict[str, Any]) -> str:
        """Extract brand from item."""
        return item.get("brand_oem") or item.get("brand") or item.get("manufacturer") or ""

    def _extract_vehicle_make(self, item: Dict[str, Any]) -> str:
        """Extract vehicle make from item."""
        return item.get("vehicle_make") or item.get("make") or item.get("car_brand") or ""

    def _extract_vehicle_model(self, item: Dict[str, Any]) -> str:
        """Extract vehicle model from item."""
        return item.get("vehicle_model") or item.get("model") or item.get("car_model") or ""

    def _extract_category(self, item: Dict[str, Any]) -> str:
        """Extract category from item."""
        return item.get("category") or item.get("type") or item.get("part_type") or ""

    def _extract_search_score(self, item: Dict[str, Any]) -> float:
        """Extract search score from item."""
        score = item.get("search_score") or item.get("score") or item.get("relevance")
        if isinstance(score, (int, float)):
            return float(score)
        return 0.5  # Default score

    def _extract_match_type(self, item: Dict[str, Any]) -> str:
        """Extract match type from item."""
        return item.get("match_type") or item.get("match_method") or "unknown"

    def _extract_matched_field(self, item: Dict[str, Any]) -> str:
        """Extract matched field from item."""
        return item.get("matched_field") or item.get("field") or "unknown"

    def _extract_price(self, item: Dict[str, Any]) -> Optional[float]:
        """Extract price from item."""
        price = item.get("price") or item.get("cost")
        if isinstance(price, (int, float)):
            return float(price)
        elif isinstance(price, str):
            # Try to extract numeric value
            import re

            numbers = re.findall(r"\d+\.?\d*", price)
            if numbers:
                return float(numbers[0])
        return None

    def _extract_availability(self, item: Dict[str, Any]) -> bool:
        """Extract availability from item."""
        availability = item.get("availability") or item.get("in_stock") or item.get("available")
        if isinstance(availability, bool):
            return availability
        elif isinstance(availability, str):
            return availability.lower() in ["true", "yes", "available", "in stock"]
        return True  # Default to available

    def _extract_description(self, item: Dict[str, Any]) -> str:
        """Extract description from item."""
        return item.get("description") or item.get("details") or item.get("summary") or ""

    def validate_response_format(self, response: AIResponse, task_type: TaskType) -> List[str]:
        """
        Validate that a response conforms to expected format.

        Args:
            response: Response to validate
            task_type: Expected task type

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not response.content:
            errors.append("Response content is empty")
            return errors

        if task_type == TaskType.SEMANTIC_SEARCH:
            if not isinstance(response.content, list):
                errors.append("Semantic search response should be a list")
            else:
                for i, item in enumerate(response.content):
                    if not isinstance(item, dict):
                        errors.append(f"Item {i} in semantic search response should be a dict")
                    elif "part_name" not in item:
                        errors.append(f"Item {i} missing required 'part_name' field")

        elif task_type == TaskType.INTELLIGENT_SEARCH:
            if not isinstance(response.content, dict):
                errors.append("Intelligent search response should be a dict")
            else:
                required_fields = ["success", "parts", "query_analysis", "suggestions"]
                for field in required_fields:
                    if field not in response.content:
                        errors.append(f"Missing required field '{field}' in intelligent search response")

        elif task_type == TaskType.QUERY_ANALYSIS:
            if not isinstance(response.content, dict):
                errors.append("Query analysis response should be a dict")
            else:
                if "intent" not in response.content:
                    errors.append("Missing required 'intent' field in query analysis response")

        elif task_type == TaskType.SUGGESTION_GENERATION:
            if not isinstance(response.content, list):
                errors.append("Suggestion response should be a list")

        elif task_type == TaskType.PART_RECOMMENDATIONS:
            if not isinstance(response.content, list):
                errors.append("Recommendation response should be a list")

        return errors
