"""
AI Query Processor - Advanced Natural Language Understanding

This module provides enhanced natural language query processing for conversational
search and complex query understanding.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.services.ai_language_processor import LanguageProcessor, Language

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Query intent types."""
    SEARCH = "search"
    PRICE_INQUIRY = "price_inquiry"
    AVAILABILITY_CHECK = "availability_check"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"
    MAINTENANCE = "maintenance"
    COMPATIBILITY = "compatibility"
    SPECIFICATION = "specification"
    UNKNOWN = "unknown"


class QueryComplexity(Enum):
    """Query complexity levels."""
    SIMPLE = "simple"      # Single part search
    MODERATE = "moderate"   # Multiple criteria
    COMPLEX = "complex"     # Multiple parts or complex requirements


@dataclass
class QueryAnalysis:
    """Comprehensive query analysis result."""
    original_query: str
    normalized_query: str
    language: Language
    language_confidence: float
    intent: QueryIntent
    complexity: QueryComplexity
    entities: Dict[str, List[str]]
    filters: Dict[str, Any]
    search_terms: List[str]
    search_variants: List[str]
    confidence: float
    suggestions: List[str]
    requires_clarification: bool
    clarification_questions: List[str]


class AIQueryProcessor:
    """
    Advanced natural language query processor for car parts search.
    """

    def __init__(self):
        self.language_processor = LanguageProcessor()
        self.intent_patterns = self._load_intent_patterns()
        self.complexity_indicators = self._load_complexity_indicators()
        self.clarification_templates = self._load_clarification_templates()

    def _load_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Load intent detection patterns."""
        return {
            QueryIntent.PRICE_INQUIRY: [
                r'\b(قیمت|price|هزینه|cost|چقدر|how much|expensive|cheap)\b',
                r'\b(ارزان|cheap|گران|expensive|مقرون|affordable)\b'
            ],
            QueryIntent.AVAILABILITY_CHECK: [
                r'\b(موجود|available|stock|inventory|دارید|have|فروش|sell)\b',
                r'\b(کی|when|زمان|time|آماده|ready)\b'
            ],
            QueryIntent.COMPARISON: [
                r'\b(مقایسه|compare|بهتر|better|تفاوت|difference|کدام|which)\b',
                r'\b(مقایسه کن|compare|کدام بهتر|which is better)\b'
            ],
            QueryIntent.RECOMMENDATION: [
                r'\b(توصیه|recommend|پیشنهاد|suggest|کدام|which|بهترین|best)\b',
                r'\b(چه|what|کدام|which|مناسب|suitable|خوب|good)\b'
            ],
            QueryIntent.MAINTENANCE: [
                r'\b(تعمیر|repair|سرویس|service|تعویض|replace|نگهداری|maintenance)\b',
                r'\b(کی|when|زمان|time|هر|every|کیلومتر|km|مایل|mile)\b'
            ],
            QueryIntent.COMPATIBILITY: [
                r'\b(سازگار|compatible|مناسب|suitable|کار|work|نصب|install)\b',
                r'\b(برای|for|ماشین|car|خودرو|vehicle)\b'
            ],
            QueryIntent.SPECIFICATION: [
                r'\b(مشخصات|specification|اندازه|size|ابعاد|dimension|وزن|weight)\b',
                r'\b(چی|what|چطور|how|چگونه|how)\b'
            ]
        }

    def _load_complexity_indicators(self) -> Dict[QueryComplexity, List[str]]:
        """Load complexity detection indicators."""
        return {
            QueryComplexity.SIMPLE: [
                r'\b(لنت|brake|فیلتر|filter)\b',  # Single part
                r'\b(چری|Chery|تیگو|Tiggo)\b'     # Single brand/model
            ],
            QueryComplexity.MODERATE: [
                r'\b(و|and|با|with|برای|for)\b',  # Multiple criteria
                r'\b(جلو|front|عقب|rear|چپ|left|راست|right)\b'  # Position
            ],
            QueryComplexity.COMPLEX: [
                r'\b(مقایسه|compare|توصیه|recommend|کدام|which)\b',  # Comparison
                r'\b(تعمیر|repair|سرویس|service|نگهداری|maintenance)\b',  # Maintenance
                r'\b(کمتر|less|بیشتر|more|بین|between|از|from|تا|to)\b'  # Range queries
            ]
        }

    def _load_clarification_templates(self) -> Dict[str, List[str]]:
        """Load clarification question templates."""
        return {
            "brand": [
                "کدام برند را ترجیح می‌دهید؟",
                "برای کدام برند جستجو می‌کنید؟",
                "Which brand are you looking for?"
            ],
            "model": [
                "کدام مدل خودرو؟",
                "برای کدام مدل؟",
                "Which vehicle model?"
            ],
            "position": [
                "جلو یا عقب؟",
                "چپ یا راست؟",
                "Front or rear? Left or right?"
            ],
            "price_range": [
                "چه محدوده قیمتی مد نظرتان است؟",
                "What's your budget range?"
            ],
            "urgency": [
                "فوری نیاز دارید؟",
                "Do you need it urgently?"
            ]
        }

    async def process_query(self, query: str) -> QueryAnalysis:
        """
        Process a natural language query comprehensively.
        
        Args:
            query: Input query string
            
        Returns:
            Comprehensive query analysis
        """
        if not query or not query.strip():
            return self._create_empty_analysis(query)

        # Basic language processing
        language, language_confidence = self.language_processor.detect_language(query)
        normalized_query = self.language_processor.normalize_text(query)
        entities = self.language_processor.extract_car_entities(query)
        search_variants = self.language_processor.create_search_variants(query)

        # Intent detection
        intent, intent_confidence = self._detect_intent(query)
        
        # Complexity analysis
        complexity = self._analyze_complexity(query)
        
        # Extract filters and search terms
        filters = self._extract_filters(query, entities)
        search_terms = self._extract_search_terms(normalized_query)
        
        # Determine if clarification is needed
        requires_clarification, clarification_questions = self._check_clarification_needed(
            query, entities, intent
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(query, entities, intent)
        
        # Calculate overall confidence
        overall_confidence = (language_confidence + intent_confidence) / 2

        return QueryAnalysis(
            original_query=query,
            normalized_query=normalized_query,
            language=language,
            language_confidence=language_confidence,
            intent=intent,
            complexity=complexity,
            entities=entities,
            filters=filters,
            search_terms=search_terms,
            search_variants=search_variants,
            confidence=overall_confidence,
            suggestions=suggestions,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions
        )

    def _detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Detect query intent with confidence score."""
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
                score += matches * 0.5  # Weight for each match
            
            if score > 0:
                intent_scores[intent] = min(score, 1.0)
        
        if not intent_scores:
            return QueryIntent.SEARCH, 0.5  # Default to search
        
        # Return intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]

    def _analyze_complexity(self, query: str) -> QueryComplexity:
        """Analyze query complexity."""
        query_lower = query.lower()
        
        # Check for complex indicators first
        for complexity, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if re.search(indicator, query_lower, re.IGNORECASE):
                    if complexity == QueryComplexity.COMPLEX:
                        return complexity
                    elif complexity == QueryComplexity.MODERATE:
                        return complexity
        
        # Check for simple indicators
        simple_indicators = self.complexity_indicators[QueryComplexity.SIMPLE]
        for indicator in simple_indicators:
            if re.search(indicator, query_lower, re.IGNORECASE):
                return QueryComplexity.SIMPLE
        
        # Default to moderate if no clear indicators
        return QueryComplexity.MODERATE

    def _extract_filters(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract filters from query and entities."""
        filters = {}
        
        # Brand filter
        if entities.get("brands"):
            filters["brand"] = entities["brands"][0]  # Take first brand
        
        # Category filter
        if entities.get("part_types"):
            filters["category"] = entities["part_types"][0]  # Take first part type
        
        # Position filter
        if entities.get("positions"):
            filters["position"] = entities["positions"][0]  # Take first position
        
        # Price range filter
        price_pattern = r'\b(\d+)\s*(تومان|تومان|ریال|dollar|dollars|\$|ریال)\b'
        price_matches = re.findall(price_pattern, query, re.IGNORECASE)
        if price_matches:
            try:
                price_value = float(price_matches[0][0])
                filters["max_price"] = price_value
            except ValueError:
                pass
        
        # Availability filter
        if any(word in query.lower() for word in ["موجود", "available", "stock"]):
            filters["available_only"] = True
        
        return filters

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query."""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "از", "در", "به", "برای", "با", "که", "این", "آن", "یک", "دو", "سه", "چند", "همه"
        }
        
        terms = query.lower().split()
        return [term for term in terms if term not in stop_words and len(term) > 1]

    def _check_clarification_needed(
        self, 
        query: str, 
        entities: Dict[str, List[str]], 
        intent: QueryIntent
    ) -> Tuple[bool, List[str]]:
        """Check if clarification is needed and generate questions."""
        clarification_questions = []
        needs_clarification = False
        
        # Check for missing brand
        if not entities.get("brands") and intent in [QueryIntent.SEARCH, QueryIntent.PRICE_INQUIRY]:
            clarification_questions.append(self.clarification_templates["brand"][0])
            needs_clarification = True
        
        # Check for missing model
        if not entities.get("models") and entities.get("brands"):
            clarification_questions.append(self.clarification_templates["model"][0])
            needs_clarification = True
        
        # Check for missing position for brake parts
        if entities.get("part_types") and any("brake" in pt.lower() for pt in entities["part_types"]):
            if not entities.get("positions"):
                clarification_questions.append(self.clarification_templates["position"][0])
                needs_clarification = True
        
        # Check for price range for price inquiries
        if intent == QueryIntent.PRICE_INQUIRY and not any(word in query.lower() for word in ["قیمت", "price", "هزینه", "cost"]):
            clarification_questions.append(self.clarification_templates["price_range"][0])
            needs_clarification = True
        
        return needs_clarification, clarification_questions

    def _generate_suggestions(
        self, 
        query: str, 
        entities: Dict[str, List[str]], 
        intent: QueryIntent
    ) -> List[str]:
        """Generate search suggestions based on query analysis."""
        suggestions = []
        
        # Add brand suggestions if missing
        if not entities.get("brands"):
            suggestions.extend(["چری", "JAC", "بریلیانس", "BYD"])
        
        # Add part type suggestions if missing
        if not entities.get("part_types"):
            suggestions.extend(["لنت ترمز", "فیلتر هوا", "فیلتر روغن", "شمع"])
        
        # Add model suggestions if brand is present but model is missing
        if entities.get("brands") and not entities.get("models"):
            brand = entities["brands"][0].lower()
            if "chery" in brand or "چری" in brand:
                suggestions.extend(["تیگو 8", "تیگو 7", "آریزو 5"])
            elif "jac" in brand or "جک" in brand:
                suggestions.extend(["J4", "J5", "J6"])
        
        # Add position suggestions for brake parts
        if entities.get("part_types") and any("brake" in pt.lower() for pt in entities["part_types"]):
            if not entities.get("positions"):
                suggestions.extend(["جلو", "عقب", "چپ", "راست"])
        
        return suggestions[:5]  # Limit to 5 suggestions

    def _create_empty_analysis(self, query: str) -> QueryAnalysis:
        """Create empty analysis for invalid queries."""
        return QueryAnalysis(
            original_query=query,
            normalized_query="",
            language=Language.UNKNOWN,
            language_confidence=0.0,
            intent=QueryIntent.UNKNOWN,
            complexity=QueryComplexity.SIMPLE,
            entities={},
            filters={},
            search_terms=[],
            search_variants=[],
            confidence=0.0,
            suggestions=[],
            requires_clarification=True,
            clarification_questions=["لطفاً سوال خود را واضح‌تر بیان کنید"]
        )

    def create_search_query(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """Create structured search query from analysis."""
        return {
            "query": analysis.normalized_query,
            "search_terms": analysis.search_terms,
            "search_variants": analysis.search_variants,
            "filters": analysis.filters,
            "intent": analysis.intent.value,
            "complexity": analysis.complexity.value,
            "language": analysis.language.value,
            "entities": analysis.entities,
            "confidence": analysis.confidence
        }

    def generate_response_suggestions(self, analysis: QueryAnalysis) -> List[str]:
        """Generate response suggestions based on query analysis."""
        suggestions = []
        
        if analysis.intent == QueryIntent.PRICE_INQUIRY:
            suggestions.extend([
                "قیمت‌های مختلف بر اساس برند",
                "مقایسه قیمت‌ها",
                "بهترین قیمت‌ها"
            ])
        elif analysis.intent == QueryIntent.AVAILABILITY_CHECK:
            suggestions.extend([
                "موجودی فعلی",
                "زمان تحویل",
                "رزرو کردن"
            ])
        elif analysis.intent == QueryIntent.RECOMMENDATION:
            suggestions.extend([
                "توصیه‌های متخصصان",
                "محصولات محبوب",
                "بررسی‌های مشتریان"
            ])
        elif analysis.intent == QueryIntent.MAINTENANCE:
            suggestions.extend([
                "برنامه تعمیرات",
                "قسمت‌های مورد نیاز",
                "هزینه تعمیرات"
            ])
        
        return suggestions

    def improve_query(self, analysis: QueryAnalysis) -> str:
        """Improve query based on analysis."""
        improved_parts = []
        
        # Add missing entities
        if analysis.entities.get("brands"):
            improved_parts.append(analysis.entities["brands"][0])
        
        if analysis.entities.get("part_types"):
            improved_parts.append(analysis.entities["part_types"][0])
        
        if analysis.entities.get("models"):
            improved_parts.append(analysis.entities["models"][0])
        
        # Add position if relevant
        if analysis.entities.get("positions"):
            improved_parts.append(analysis.entities["positions"][0])
        
        # Combine parts
        if improved_parts:
            return " ".join(improved_parts)
        
        return analysis.normalized_query
