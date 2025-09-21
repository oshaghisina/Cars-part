"""
AI Service for enhanced search and part recommendations using OpenAI.
"""

import openai
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
import json
import re

from app.core.config import settings
from app.db.models import Part, Price, Synonym
from app.services.search import SearchService

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered search and recommendation service."""

    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)
        self.client = None

        # Initialize OpenAI client if API key is provided
        if settings.openai_api_key:
            try:
                openai.api_key = settings.openai_api_key
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e})
                self.client = None
        else:
            logger.warning(OpenAI API key not provided)

    def is_available(self) -> bool:
        Check if AI service is available.""
        return self.client is not None and settings.ai_enabled

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        if not self.is_available():
            return []

        try:
            response = self.client.embeddings.create(
                model=settings.openai_embedding_model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error creating embeddings: {e})
            return []

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        Calculate cosine similarity between two vectors.
        try:
            a_np = np.array(a)
            b_np = np.array(b)
            return float(np.dot(a_np, b_np) /
                         (np.linalg.norm(a_np) * np.linalg.norm(b_np)))
        except Exception:
            return 0.0

    def semantic_search(
            self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using OpenAI embeddings."""
        if not self.is_available():
            logger.warning(
                "AI service not available, falling back to regular search")
            return self.search_service.search_parts(query, limit)

        try:
            # Get all parts with their descriptions
            parts = self.db.query(Part).filter(Part.status == 'active').all()

            if not parts:
                return []

            # Create part descriptions for embedding
            part_descriptions = []
            part_data = []

            for part in parts:
                description = f"{
                    part.part_name} {
                    part.brand_oem} {
                    part.vehicle_make} {
                    part.vehicle_model} {part.category}
                if part.oem_code:
                    description += f {part.oem_code}
                if part.vehicle_trim:
                    description += f {part.vehicle_trim}
                if part.position:
                    description += f {part.position}

                part_descriptions.append(description)
                part_data.append(part)

            # Create embeddings
            part_embeddings = self._create_embeddings(part_descriptions)
            query_embedding = self._create_embeddings([query])

            if not part_embeddings or not query_embedding:
                logger.warning(
                    Failed to create embeddings, falling back to regular search)
                return self.search_service.search_parts(query, limit)

            # Calculate similarities
            similarities = []
            for i, part_embedding in enumerate(part_embeddings):
                similarity = self._cosine_similarity(
                    query_embedding[0], part_embedding)
                similarities.append((similarity, part_data[i]))

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)

            results = []
            for similarity, part in similarities[:limit]:
                if similarity > 0.7:  # Minimum similarity threshold
                    # Format the part object properly
                    part_dict = {
                        "part": part,
                        "score": similarity,
                        "match_type": "semantic",
                        "matched_field": "ai_similarity"
                    }
                    result = self.search_service.format_search_result(
                        part_dict)
                    result['search_score'] = similarity
                    result['match_type'] = 'semantic'
                    result['matched_field'] = 'ai_similarity'
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e})
            return self.search_service.search_parts(query, limit)

    def intelligent_search(
            self, query: str, limit: int = 10) -> Dict[str, Any]:
        Perform intelligent search with query understanding and expansion.
        if not self.is_available():
            return {
                "success": True,
                "parts": self.search_service.search_parts(query, limit),
                "query_analysis": None,
                "suggestions": [],
                "search_type": "basic"
            }

        try:
            # Analyze the query
            query_analysis = self._analyze_query(query)

            # Expand the query with synonyms and related terms
            expanded_queries = self._expand_query(query, query_analysis)

            # Perform search with original and expanded queries
            all_results = []
            seen_part_ids = set()

            # Limit to top 3 expansions
            for expanded_query in expanded_queries[:3]:
                if expanded_query != query:  # Skip original query to avoid duplicates
                    results = self.semantic_search(expanded_query, limit // 2)
                    for result in results:
                        if result['id'] not in seen_part_ids:
                            all_results.append(result)
                            seen_part_ids.add(result['id'])

            # Add original query results
            original_results = self.semantic_search(query, limit)
            for result in original_results:
                if result['id'] not in seen_part_ids:
                    all_results.append(result)
                    seen_part_ids.add(result['id'])

            # Generate suggestions
            suggestions = self._generate_suggestions(
                query, query_analysis, all_results)

            return {
                "success": True,
                "parts": all_results[:limit],
                "query_analysis": query_analysis,
                "suggestions": suggestions,
                "search_type": "intelligent"
            }

        except Exception as e:
            logger.error(f"Error in intelligent search: {e})
            return {
                success: False,
                parts: [],
                query_analysis: None,
                "suggestions": [],
                "search_type": "basic",
                "error": str(e)
            }

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze user query to extract intent and entities."""
        if not self.is_available():
            return {"intent": "search", "entities": [], "language": "unknown"}

        try:
            prompt = f"
            Analyze this car parts search query and extract:
            1. Intent (what the user wants to find)
            2. Car brand/model mentioned
            3. Part type/category
            4. Language (Persian/English)
            5. Specific requirements (front/rear, left/right, etc.)

            Query: {query}

            Respond in JSON format:
            {{
                intent: search_for_part,
                "car_brand": "Chery",
                "car_model": "Tiggo 8",
                "part_type": "brake_pad",
                "language": "persian",
                "position": "front",
                "specific_requirements": []
            }}
            """

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )

            analysis_text = response.choices[0].message.content.strip()

            # Try to parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "intent": "search",
                    "car_brand": self._extract_brand(query),
                    "car_model": self._extract_model(query),
                    "part_type": self._extract_part_type(query),
                    "language": "persian" if self._is_persian(query) else "english",
                    "position": self._extract_position(query),
                    "specific_requirements": []}

        except Exception as e:
            logger.error(f"Error analyzing query: {e})
            return {intent: search, entities: [], "language": "unknown"}

    def _expand_query(self, query: str, analysis: Dict[str, Any]) -> List[str]:
        """Expand query with synonyms and related terms."""
        expanded_queries = [query]  # Always include original

        try:
            # Generate synonyms and related terms
            prompt = f"
            Generate 3 alternative search queries for car parts based on this query:
            Original: {query}
            Analysis: {json.dumps(analysis, ensure_ascii=False)}

            Generate variations that might help find the same or related parts:
            1. Use different terminology
            2. Include common synonyms
            3. Add related part categories

            Respond with just 3 queries, one per line, no explanations.
            

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )

            expansions = response.choices[0].message.content.strip().split(
                '\n')
            expanded_queries.extend([exp.strip()
                                    for exp in expansions if exp.strip()])

        except Exception as e:
            logger.error(f"Error expanding query: {e})

        return expanded_queries[:4]  # Limit to 4 total queries

    def _generate_suggestions(self,
                              query: str,
                              analysis: Dict[str,
                                             Any],
                              results: List[Dict[str,
                                                 Any]]) -> List[str]:
        Generate smart suggestions based on search results.
        if not self.is_available() or not results:
            return []

        try:
            # Extract categories from results
            categories = list(set([result.get('category', '')
                              for result in results if result.get('category')]))
            brands = list(set([result.get('brand_oem', '')
                          for result in results if result.get('brand_oem')]))

            prompt = f"
            Based on this car parts search query and results, generate 3 helpful suggestions:

            Query: {query}
            Found categories: {', '.join(categories)}
            Found brands: {', '.join(brands)}

            Generate suggestions like:
            - Related parts the user might need
            - Alternative brands for the same part
            - Complementary parts for maintenance

            Respond with just 3 suggestions, one per line, in the same language as the query.
            "

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.4
            )

            suggestions = response.choices[0].message.content.strip().split(
                '\n')
            return [s.strip() for s in suggestions if s.strip()][:3]

        except Exception as e:
            logger.error(f"Error generating suggestions: {e})
            return []

    def get_part_recommendations(
            self, part_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        Get AI-powered part recommendations based on a specific part.
        if not self.is_available():
            return []

        try:
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return []

            # Create part description for similarity search
            part_description = f"{
                part.part_name} {
                part.brand_oem} {
                part.vehicle_make} {
                part.vehicle_model} {part.category}

            # Find similar parts using semantic search
            similar_parts = self.semantic_search(part_description, limit * 2)

            # Filter out the original part and get top recommendations
            recommendations = [
                result for result in similar_parts
                if result['id'] != part_id
            ][:limit]

            return recommendations

        except Exception as e:
            logger.error(fError getting part recommendations: {e})
            return []

    def _extract_brand(self, text: str) -> Optional[str]:
        "Extract car brand from text."""
        brands = [
            'Chery',
            'JAC',
            'Brilliance',
            'BYD',
            'Geely',
            'Great Wall',
            'MG',
            'Chery',
            'JAC',
            'Brilliance']
        for brand in brands:
            if brand.lower() in text.lower():
                return brand
        return None

    def _extract_model(self, text: str) -> Optional[str]:
        """Extract car model from text."""
        models = ['Tiggo 8', 'X22', 'H330', 'Arizo 5', 'Tiggo 7', 'Arrizo 3']
        for model in models:
            if model.lower() in text.lower():
                return model
        return None

    def _extract_part_type(self, text: str) -> Optional[str]:
        """Extract part type from text."""
        part_types = {
            'brake': ['لنت', 'ترمز', 'brake', 'pad'],
            'filter': ['فیلتر', 'filter'],
            'engine': ['موتور', 'engine'],
            'suspension': ['تعلیق', 'suspension'],
            'transmission': ['گیربکس', 'transmission']
        }

        text_lower = text.lower()
        for part_type, keywords in part_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return part_type
        return None

    def _extract_position(self, text: str) -> Optional[str]:
        """Extract position (front/rear, left/right) from text."""
        positions = [
            'جلو',
            'عقب',
            'چپ',
            'راست',
            'front',
            'rear',
            'left',
            'right']
        text_lower = text.lower()
        for position in positions:
            if position in text_lower:
                return position
        return None

    def _is_persian(self, text: str) -> bool:
        """Check if text contains Persian characters."""
        persian_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(persian_pattern.search(text))

    def bulk_intelligent_search(
            self, queries: List[str], limit_per_query: int = 5) -> List[Dict[str, Any]]:
        """Perform intelligent search for multiple queries."""
        results = []

        for query in queries:
            if query.strip():
                result = self.intelligent_search(
                    query.strip(), limit_per_query)
                results.append({
                    "query": query,
                    "success": result["success"],
                    "parts": result["parts"],
                    "query_analysis": result.get("query_analysis"),
                    "suggestions": result.get("suggestions", []),
                    "search_type": result.get("search_type", "basic")
                })
            else:
                results.append({
                    "query": query,
                    "success": False,
                    "parts": [],
                    "query_analysis": None,
                    "suggestions": [],
                    "search_type": "basic",
                    "error": "Empty query"
                })

        return results
