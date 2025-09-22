"""
AI Orchestrator Epic E3 Extensions - Advanced AI Features

This module contains the Epic E3 extensions for the AI Orchestrator,
providing advanced AI features and integration capabilities.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.ai_hybrid_search import HybridSearchEngine, SearchType
from app.services.ai_language_processor import LanguageProcessor
from app.services.ai_query_processor import AIQueryProcessor
from app.services.ai_recommendations import AIRecommendationsEngine, UserProfile
from app.services.ai_tracing import TraceContext

logger = logging.getLogger(__name__)


class AIOrchestratorE3Extensions:
    """
    Epic E3 extensions for AI Orchestrator.
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.language_processor = LanguageProcessor()
        self.hybrid_search_engine = HybridSearchEngine()
        self.recommendations_engine = AIRecommendationsEngine()
        self.query_processor = AIQueryProcessor()

    async def hybrid_search(
        self,
        query: str,
        parts: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        search_type: str = "hybrid",
        limit: int = 20,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic, keyword, and filter-based search.
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping hybrid search.")
            return []

        with TraceContext(
            self.orchestrator.tracer,
            "hybrid_search",
            user_id=user_id,
            query=query[:50],
            search_type=search_type,
            parts_count=len(parts),
        ):
            start_time = time.time()

            try:
                # Convert string search_type to enum
                search_type_enum = SearchType.HYBRID
                if search_type == "semantic":
                    search_type_enum = SearchType.SEMANTIC
                elif search_type == "keyword":
                    search_type_enum = SearchType.KEYWORD
                elif search_type == "filter":
                    search_type_enum = SearchType.FILTER

                # Perform hybrid search
                results = await self.hybrid_search_engine.search(
                    query=query,
                    parts=parts,
                    filters=filters,
                    search_type=search_type_enum,
                    **kwargs,
                )

                # Convert SearchResult objects to dictionaries
                search_results = []
                for result in results:
                    search_results.append(
                        {
                            "part_id": result.part_id,
                            "part_name": result.part_name,
                            "brand_oem": result.brand_oem,
                            "vehicle_make": result.vehicle_make,
                            "vehicle_model": result.vehicle_model,
                            "category": result.category,
                            "price": result.price,
                            "availability": result.availability,
                            "search_score": result.search_score,
                            "match_type": result.match_type,
                            "matched_fields": result.matched_fields,
                            "raw_data": result.raw_data,
                        }
                    )

                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="hybrid_search",
                    task_type="hybrid_search",
                    duration_ms=duration_ms,
                    success=True,
                    cost=0.0,
                )

                logger.info(
                    f"Hybrid search completed successfully. Found {
                        len(search_results)} results.")
                return search_results

            except Exception as e:
                # Record error metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="hybrid_search",
                    task_type="hybrid_search",
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                )

                logger.error(f"Error in hybrid search: {e}")
                return []

    async def get_smart_recommendations(
        self,
        part_id: int,
        part_data: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        recommendation_types: Optional[List[str]] = None,
        limit: int = 5,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered smart recommendations for a part.
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping recommendations.")
            return []

        with TraceContext(
            self.orchestrator.tracer,
            "smart_recommendations",
            user_id=user_id,
            part_id=part_id,
            recommendation_types=recommendation_types,
        ):
            start_time = time.time()

            try:
                # Convert user profile if provided
                user_profile_obj = None
                if user_profile:
                    user_profile_obj = UserProfile(
                        user_id=user_id or "anonymous",
                        purchase_history=user_profile.get("purchase_history", []),
                        search_history=user_profile.get("search_history", []),
                        preferences=user_profile.get("preferences", {}),
                        vehicle_info=user_profile.get("vehicle_info"),
                    )

                # Convert recommendation types
                from app.services.ai_recommendations import RecommendationType

                rec_types = None
                if recommendation_types:
                    rec_types = []
                    for rt in recommendation_types:
                        if hasattr(RecommendationType, rt.upper()):
                            rec_types.append(getattr(RecommendationType, rt.upper()))

                # Get recommendations
                recommendations = await self.recommendations_engine.get_recommendations(
                    part_id=part_id,
                    part_data=part_data,
                    user_profile=user_profile_obj,
                    recommendation_types=rec_types,
                    limit=limit,
                )

                # Convert Recommendation objects to dictionaries
                rec_results = []
                for rec in recommendations:
                    rec_results.append(
                        {
                            "part_id": rec.part_id,
                            "part_name": rec.part_name,
                            "brand_oem": rec.brand_oem,
                            "vehicle_make": rec.vehicle_make,
                            "vehicle_model": rec.vehicle_model,
                            "category": rec.category,
                            "price": rec.price,
                            "availability": rec.availability,
                            "recommendation_score": rec.recommendation_score,
                            "recommendation_type": rec.recommendation_type.value,
                            "reason": rec.reason,
                            "confidence": rec.confidence,
                            "raw_data": rec.raw_data,
                        }
                    )

                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="recommendations_engine",
                    task_type="recommendations",
                    duration_ms=duration_ms,
                    success=True,
                    cost=0.0,
                )

                logger.info(
                    f"Smart recommendations completed successfully. Generated {
                        len(rec_results)} recommendations.")
                return rec_results

            except Exception as e:
                # Record error metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="recommendations_engine",
                    task_type="recommendations",
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                )

                logger.error(f"Error in smart recommendations: {e}")
                return []

    async def process_natural_language_query(
        self, query: str, user_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Process natural language query with advanced understanding.
        """
        if not getattr(settings, "ai_gateway_enabled", False):
            logger.debug("AI Gateway disabled. Skipping query processing.")
            return {"success": False, "error": "AI Gateway disabled", "query": query}

        with TraceContext(self.orchestrator.tracer, "natural_language_query", user_id=user_id, query=query[:50]):
            start_time = time.time()

            try:
                # Process the query
                analysis = await self.query_processor.process_query(query)

                # Create structured search query
                search_query = self.query_processor.create_search_query(analysis)

                # Generate response suggestions
                response_suggestions = self.query_processor.generate_response_suggestions(analysis)

                # Improve query if needed
                improved_query = self.query_processor.improve_query(analysis)

                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="query_processor",
                    task_type="query_analysis",
                    duration_ms=duration_ms,
                    success=True,
                    cost=0.0,
                )

                result = {
                    "success": True,
                    "original_query": analysis.original_query,
                    "normalized_query": analysis.normalized_query,
                    "improved_query": improved_query,
                    "language": analysis.language.value,
                    "language_confidence": analysis.language_confidence,
                    "intent": analysis.intent.value,
                    "complexity": analysis.complexity.value,
                    "entities": analysis.entities,
                    "filters": analysis.filters,
                    "search_terms": analysis.search_terms,
                    "search_variants": analysis.search_variants,
                    "confidence": analysis.confidence,
                    "suggestions": analysis.suggestions,
                    "response_suggestions": response_suggestions,
                    "requires_clarification": analysis.requires_clarification,
                    "clarification_questions": analysis.clarification_questions,
                    "search_query": search_query,
                }

                logger.info("Natural language query processing completed successfully.")
                return result

            except Exception as e:
                # Record error metrics
                duration_ms = (time.time() - start_time) * 1000
                self.orchestrator.metrics.record_request(
                    provider="query_processor",
                    task_type="query_analysis",
                    duration_ms=duration_ms,
                    success=False,
                    error_type=type(e).__name__,
                )

                logger.error(f"Error in natural language query processing: {e}")
                return {"success": False, "error": str(e), "query": query}

    def get_language_analysis(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive language analysis for text.
        """
        try:
            # Detect language
            language, confidence = self.language_processor.detect_language(text)

            # Extract entities
            entities = self.language_processor.extract_car_entities(text)

            # Create search variants
            variants = self.language_processor.create_search_variants(text)

            # Normalize text
            normalized = self.language_processor.normalize_text(text)

            return {
                "original_text": text,
                "normalized_text": normalized,
                "language": language.value,
                "language_confidence": confidence,
                "entities": entities,
                "search_variants": variants,
                "contains_persian": language.value == "persian",
                "contains_english": language.value == "english",
                "is_mixed": language.value == "mixed",
            }

        except Exception as e:
            logger.error(f"Error in language analysis: {e}")
            return {"original_text": text, "error": str(e)}
