"""
AI Hybrid Search Engine - Advanced Search Capabilities

This module implements a hybrid search system that combines semantic search,
keyword matching, and filter-based search for optimal results.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.services.ai_language_processor import LanguageProcessor, Language
from app.services.ai_provider import TaskType

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """Types of search methods."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    FILTER = "filter"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Represents a search result with scoring."""
    part_id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    category: str
    price: Optional[float]
    availability: bool
    search_score: float
    match_type: str
    matched_fields: List[str]
    raw_data: Dict[str, Any]


@dataclass
class SearchConfig:
    """Configuration for hybrid search."""
    semantic_weight: float = 0.4
    keyword_weight: float = 0.3
    filter_weight: float = 0.3
    min_score_threshold: float = 0.1
    max_results: int = 20
    enable_fuzzy_matching: bool = True
    fuzzy_threshold: float = 0.8


class HybridSearchEngine:
    """
    Advanced hybrid search engine combining multiple search methods.
    """

    def __init__(self, config: Optional[SearchConfig] = None):
        self.config = config or SearchConfig()
        self.language_processor = LanguageProcessor()

    async def search(
        self,
        query: str,
        parts: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        search_type: SearchType = SearchType.HYBRID,
        **kwargs
    ) -> List[SearchResult]:
        """
        Perform hybrid search on parts.
        
        Args:
            query: Search query
            parts: List of parts to search
            filters: Optional filters to apply
            search_type: Type of search to perform
            **kwargs: Additional search parameters
            
        Returns:
            List of search results sorted by relevance
        """
        if not query or not parts:
            return []

        # Analyze the query
        query_analysis = self.language_processor.analyze_query_intent(query)
        
        # Apply filters if provided
        filtered_parts = self._apply_filters(parts, filters) if filters else parts
        
        # Perform search based on type
        if search_type == SearchType.SEMANTIC:
            results = await self._semantic_search(query, filtered_parts, query_analysis)
        elif search_type == SearchType.KEYWORD:
            results = self._keyword_search(query, filtered_parts, query_analysis)
        elif search_type == SearchType.FILTER:
            results = self._filter_search(query, filtered_parts, query_analysis)
        else:  # HYBRID
            results = await self._hybrid_search(query, filtered_parts, query_analysis)
        
        # Sort by score and return top results
        results.sort(key=lambda x: x.search_score, reverse=True)
        return results[:self.config.max_results]

    async def _hybrid_search(
        self, 
        query: str, 
        parts: List[Dict[str, Any]], 
        query_analysis: Dict[str, Any]
    ) -> List[SearchResult]:
        """Perform hybrid search combining all methods."""
        # Get results from each search method
        semantic_results = await self._semantic_search(query, parts, query_analysis)
        keyword_results = self._keyword_search(query, parts, query_analysis)
        filter_results = self._filter_search(query, parts, query_analysis)
        
        # Combine and re-score results
        combined_results = self._combine_search_results(
            semantic_results, keyword_results, filter_results
        )
        
        return combined_results

    async def _semantic_search(
        self, 
        query: str, 
        parts: List[Dict[str, Any]], 
        query_analysis: Dict[str, Any]
    ) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        # This would integrate with the AI Gateway for semantic search
        # For now, we'll implement a basic text similarity approach
        
        results = []
        query_lower = query.lower()
        
        for part in parts:
            # Create searchable text
            searchable_text = self._create_searchable_text(part)
            
            # Calculate semantic similarity (simplified)
            similarity = self._calculate_text_similarity(query_lower, searchable_text)
            
            if similarity > self.config.min_score_threshold:
                result = SearchResult(
                    part_id=part.get("id", 0),
                    part_name=part.get("part_name", ""),
                    brand_oem=part.get("brand_oem", ""),
                    vehicle_make=part.get("vehicle_make", ""),
                    vehicle_model=part.get("vehicle_model", ""),
                    category=part.get("category", ""),
                    price=part.get("price"),
                    availability=part.get("availability", True),
                    search_score=similarity * self.config.semantic_weight,
                    match_type="semantic",
                    matched_fields=["ai_similarity"],
                    raw_data=part
                )
                results.append(result)
        
        return results

    def _keyword_search(
        self, 
        query: str, 
        parts: List[Dict[str, Any]], 
        query_analysis: Dict[str, Any]
    ) -> List[SearchResult]:
        """Perform keyword-based search."""
        results = []
        query_terms = self._extract_search_terms(query)
        
        for part in parts:
            score = 0.0
            matched_fields = []
            
            # Search in different fields
            field_scores = {
                "part_name": self._calculate_field_score(query_terms, part.get("part_name", "")),
                "brand_oem": self._calculate_field_score(query_terms, part.get("brand_oem", "")),
                "vehicle_make": self._calculate_field_score(query_terms, part.get("vehicle_make", "")),
                "vehicle_model": self._calculate_field_score(query_terms, part.get("vehicle_model", "")),
                "category": self._calculate_field_score(query_terms, part.get("category", ""))
            }
            
            # Calculate weighted score
            weights = {
                "part_name": 0.4,
                "brand_oem": 0.3,
                "vehicle_make": 0.15,
                "vehicle_model": 0.1,
                "category": 0.05
            }
            
            for field, field_score in field_scores.items():
                if field_score > 0:
                    score += field_score * weights[field]
                    matched_fields.append(field)
            
            if score > self.config.min_score_threshold:
                result = SearchResult(
                    part_id=part.get("id", 0),
                    part_name=part.get("part_name", ""),
                    brand_oem=part.get("brand_oem", ""),
                    vehicle_make=part.get("vehicle_make", ""),
                    vehicle_model=part.get("vehicle_model", ""),
                    category=part.get("category", ""),
                    price=part.get("price"),
                    availability=part.get("availability", True),
                    search_score=score * self.config.keyword_weight,
                    match_type="keyword",
                    matched_fields=matched_fields,
                    raw_data=part
                )
                results.append(result)
        
        return results

    def _filter_search(
        self, 
        query: str, 
        parts: List[Dict[str, Any]], 
        query_analysis: Dict[str, Any]
    ) -> List[SearchResult]:
        """Perform filter-based search using extracted entities."""
        results = []
        entities = query_analysis.get("entities", {})
        
        for part in parts:
            score = 0.0
            matched_fields = []
            
            # Match brands
            if entities.get("brands"):
                part_brand = part.get("brand_oem", "").lower()
                vehicle_make = part.get("vehicle_make", "").lower()
                for brand in entities["brands"]:
                    if brand.lower() in part_brand or brand.lower() in vehicle_make:
                        score += 0.3
                        matched_fields.append("brand")
            
            # Match part types
            if entities.get("part_types"):
                part_name = part.get("part_name", "").lower()
                category = part.get("category", "").lower()
                for part_type in entities["part_types"]:
                    if part_type.lower() in part_name or part_type.lower() in category:
                        score += 0.4
                        matched_fields.append("part_type")
            
            # Match models
            if entities.get("models"):
                vehicle_model = part.get("vehicle_model", "").lower()
                for model in entities["models"]:
                    if model.lower() in vehicle_model:
                        score += 0.2
                        matched_fields.append("model")
            
            # Match positions
            if entities.get("positions"):
                part_name = part.get("part_name", "").lower()
                for position in entities["positions"]:
                    if position.lower() in part_name:
                        score += 0.1
                        matched_fields.append("position")
            
            if score > self.config.min_score_threshold:
                result = SearchResult(
                    part_id=part.get("id", 0),
                    part_name=part.get("part_name", ""),
                    brand_oem=part.get("brand_oem", ""),
                    vehicle_make=part.get("vehicle_make", ""),
                    vehicle_model=part.get("vehicle_model", ""),
                    category=part.get("category", ""),
                    price=part.get("price"),
                    availability=part.get("availability", True),
                    search_score=score * self.config.filter_weight,
                    match_type="filter",
                    matched_fields=matched_fields,
                    raw_data=part
                )
                results.append(result)
        
        return results

    def _combine_search_results(
        self, 
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        filter_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Combine results from different search methods."""
        # Create a dictionary to store combined results
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            key = result.part_id
            if key not in combined:
                combined[key] = result
            else:
                combined[key].search_score += result.search_score
                combined[key].matched_fields.extend(result.matched_fields)
                combined[key].match_type = "hybrid"
        
        # Add keyword results
        for result in keyword_results:
            key = result.part_id
            if key not in combined:
                combined[key] = result
            else:
                combined[key].search_score += result.search_score
                combined[key].matched_fields.extend(result.matched_fields)
                if combined[key].match_type != "hybrid":
                    combined[key].match_type = "hybrid"
        
        # Add filter results
        for result in filter_results:
            key = result.part_id
            if key not in combined:
                combined[key] = result
            else:
                combined[key].search_score += result.search_score
                combined[key].matched_fields.extend(result.matched_fields)
                if combined[key].match_type != "hybrid":
                    combined[key].match_type = "hybrid"
        
        # Remove duplicate matched fields
        for result in combined.values():
            result.matched_fields = list(set(result.matched_fields))
        
        return list(combined.values())

    def _apply_filters(self, parts: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to parts list."""
        filtered_parts = parts.copy()
        
        # Brand filter
        if "brand" in filters and filters["brand"]:
            brand = filters["brand"].lower()
            filtered_parts = [
                p for p in filtered_parts 
                if brand in p.get("brand_oem", "").lower() or brand in p.get("vehicle_make", "").lower()
            ]
        
        # Category filter
        if "category" in filters and filters["category"]:
            category = filters["category"].lower()
            filtered_parts = [
                p for p in filtered_parts 
                if category in p.get("category", "").lower()
            ]
        
        # Price range filter
        if "min_price" in filters and filters["min_price"] is not None:
            min_price = float(filters["min_price"])
            filtered_parts = [
                p for p in filtered_parts 
                if p.get("price") is not None and p.get("price", 0) >= min_price
            ]
        
        if "max_price" in filters and filters["max_price"] is not None:
            max_price = float(filters["max_price"])
            filtered_parts = [
                p for p in filtered_parts 
                if p.get("price") is not None and p.get("price", 0) <= max_price
            ]
        
        # Availability filter
        if "available_only" in filters and filters["available_only"]:
            filtered_parts = [
                p for p in filtered_parts 
                if p.get("availability", True)
            ]
        
        return filtered_parts

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query."""
        # Normalize and split query
        normalized = self.language_processor.normalize_text(query)
        terms = normalized.lower().split()
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "از", "در", "به", "برای", "با", "که", "این", "آن", "یک", "دو", "سه"
        }
        
        return [term for term in terms if term not in stop_words and len(term) > 1]

    def _calculate_field_score(self, query_terms: List[str], field_value: str) -> float:
        """Calculate relevance score for a field."""
        if not field_value:
            return 0.0
        
        field_lower = field_value.lower()
        score = 0.0
        
        for term in query_terms:
            if term in field_lower:
                # Exact match gets higher score
                if field_lower == term:
                    score += 1.0
                elif field_lower.startswith(term) or field_lower.endswith(term):
                    score += 0.8
                else:
                    score += 0.6
        
        # Normalize by number of terms
        return score / len(query_terms) if query_terms else 0.0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard similarity."""
        if not text1 or not text2:
            return 0.0
        
        # Tokenize texts
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0

    def _create_searchable_text(self, part: Dict[str, Any]) -> str:
        """Create searchable text from part data."""
        fields = [
            part.get("part_name", ""),
            part.get("brand_oem", ""),
            part.get("vehicle_make", ""),
            part.get("vehicle_model", ""),
            part.get("category", ""),
            part.get("description", "")
        ]
        
        return " ".join(filter(None, fields)).lower()

    def get_search_suggestions(
        self, 
        query: str, 
        parts: List[Dict[str, Any]], 
        limit: int = 5
    ) -> List[str]:
        """Get search suggestions based on query and available parts."""
        if not query or len(query) < 2:
            return []
        
        suggestions = set()
        query_lower = query.lower()
        
        # Extract unique values from parts
        for part in parts:
            # Add part names that contain the query
            part_name = part.get("part_name", "")
            if query_lower in part_name.lower():
                suggestions.add(part_name)
            
            # Add brands that contain the query
            brand = part.get("brand_oem", "")
            if query_lower in brand.lower():
                suggestions.add(brand)
            
            # Add models that contain the query
            model = part.get("vehicle_model", "")
            if query_lower in model.lower():
                suggestions.add(model)
        
        # Sort by relevance and return top suggestions
        sorted_suggestions = sorted(suggestions, key=lambda x: len(x))
        return sorted_suggestions[:limit]
