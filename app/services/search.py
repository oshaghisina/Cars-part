"""Search service for parts lookup."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from rapidfuzz import fuzz
from app.db.models import Part, Price, Synonym
from app.core.config import settings


class SearchService:
    """Service for searching parts with various strategies."""

    def __init__(self, db: Session):
        self.db = db

    def search_parts(self, query: str, limit: int = 10) -> List[dict]:
        """
        Search for parts using multiple strategies including AI.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of part dictionaries with search scores
        """
        query = query.strip().lower()
        if not query:
            return []

        # Try AI-enhanced search first if available
        if settings.ai_enabled:
            try:
                from app.services.ai_service import AIService
                ai_service = AIService(self.db)
                if ai_service.is_available():
                    ai_results = ai_service.semantic_search(query, limit)
                    if ai_results:
                        return ai_results
            except Exception as e:
                print(f"AI search failed, falling back to basic search: {e}"")

        # Fallback to basic search strategies
        results = []

        # 1. Exact OEM code match
        oem_results = self._search_by_oem_code(query)
        results.extend(oem_results)

        # 2. Synonym-based search
        synonym_results = self._search_by_synonyms(query)
        results.extend(synonym_results)

        # 3. Fuzzy search on part names and descriptions
        fuzzy_results = self._fuzzy_search(query)
        results.extend(fuzzy_results)

        # Remove duplicates and sort by score
        unique_results = self._deduplicate_and_score(results)

        # Return top results
        return unique_results[:limit]

    def _search_by_oem_code(self, query: str) -> List[dict]:
        """Search by exact OEM code match."""
        parts = self.db.query(Part).filter(
            or_(
                Part.oem_code.ilike(f"%{query}"%"),
                Part.alt_codes.ilike(f"%{query}"%")
            ),
            Part.status == "active"
        ).all()

        results = []
        for part in parts:
            results.append({
                "part": part,
                "score": 1.0,
                "match_type": "oem_code",
                "matched_field": "oem_code"
            })

        return results

    def _search_by_synonyms(self, query: str) -> List[dict]:
        """Search using synonyms table."""
        # Search Persian synonyms
        persian_synonyms = self.db.query(Synonym).filter(
            Synonym.keyword.ilike(f"%{query}"%"),
            Synonym.lang == "fa"
        ).all()

        # Search English synonyms
        english_synonyms = self.db.query(Synonym).filter(
            Synonym.keyword.ilike(f"%{query}"%"),
            Synonym.lang == "en"
        ).all()

        results = []

        # Process Persian matches (higher priority)
        for synonym in persian_synonyms:
            if synonym.part_id:
                part = self.db.query(Part).filter(
                    Part.id == synonym.part_id,
                    Part.status == "active"
                ).first()

                if part:
                    # Calculate score based on synonym weight and match quality
                    match_score = fuzz.ratio(query, synonym.keyword) / 100.0
                    score = synonym.weight * match_score

                    results.append({
                        "part": part,
                        "score": score,
                        "match_type": "synonym",
                        "matched_field": "persian_synonym",
                        "synonym": synonym.keyword
                    })

        # Process English matches (lower priority)
        for synonym in english_synonyms:
            if synonym.part_id:
                part = self.db.query(Part).filter(
                    Part.id == synonym.part_id,
                    Part.status == "active"
                ).first()

                if part:
                    match_score = fuzz.ratio(query, synonym.keyword) / 100.0
                    score = synonym.weight * match_score * 0.8  # Lower weight for English

                    results.append({
                        "part": part,
                        "score": score,
                        "match_type": "synonym",
                        "matched_field": "english_synonym",
                        "synonym": synonym.keyword
                    })

        return results

    def _fuzzy_search(self, query: str) -> List[dict]:
        """Fuzzy search on part names and descriptions."""
        parts = self.db.query(Part).filter(Part.status == "active").all()

        results = []
        for part in parts:
            # Calculate fuzzy match scores
            name_score = fuzz.ratio(query, part.part_name.lower())
            vehicle_score = fuzz.ratio(query, part.vehicle_model.lower())
            category_score = fuzz.ratio(query, part.category.lower())

            # Take the highest score
            max_score = max(name_score, vehicle_score, category_score)

            # Only include if score is above threshold
            if max_score >= 60:  # 60% similarity threshold
                # Normalize score
                normalized_score = max_score / 100.0 * 0.7  # Lower weight for fuzzy matches

                matched_field = "part_name"
                if vehicle_score == max_score:
                    matched_field = "vehicle_model"
                elif category_score == max_score:
                    matched_field = "category"

                results.append({
                    "part": part,
                    "score": normalized_score,
                    "match_type": "fuzzy",
                    "matched_field": matched_field,
                    "raw_score": max_score
                })

        return results

    def _deduplicate_and_score(self, results: List[dict]) -> List[dict]:
        """Remove duplicates and sort by score."""
        seen_parts = {}

        for result in results:
            part_id = result["part"].id

            if part_id not in seen_parts:
                seen_parts[part_id] = result
            else:
                # Keep the result with higher score
                if result["score"] > seen_parts[part_id]["score"]:
                    seen_parts[part_id] = result

        # Sort by score (descending)
        unique_results = list(seen_parts.values())
        unique_results.sort(key=lambda x: x["score"], reverse=True)

        return unique_results

    def get_part_prices(self, part_id: int) -> List[dict]:
        """Get active prices for a part."""
        from datetime import date

        today = date.today()
        prices = self.db.query(Price).filter(
            Price.part_id == part_id,
            or_(
                Price.valid_to.is_(None),
                and_(
                    Price.valid_from.isnot(None),
                    Price.valid_to.isnot(None),
                    Price.valid_from <= today,
                    Price.valid_to >= today
                )
            )
        ).order_by(Price.price.asc()).all()

        return [
            {
                "id": price.id,
                "seller_name": price.seller_name,
                "price": float(price.price),
                "currency": price.currency,
                "min_order_qty": price.min_order_qty,
                "available_qty": price.available_qty,
                "warranty": price.warranty,
                "source_type": price.source_type,
                "note": price.note
            }
            for price in prices
        ]

    def format_search_result(self, result: dict) -> dict:
        """Format search result for API response."""
        part = result["part"]
        prices = self.get_part_prices(part.id)

        return {
            "id": part.id,
            "part_name": part.part_name,
            "brand_oem": part.brand_oem,
            "vehicle_make": part.vehicle_make,
            "vehicle_model": part.vehicle_model,
            "vehicle_trim": part.vehicle_trim,
            "oem_code": part.oem_code,
            "category": part.category,
            "subcategory": part.subcategory,
            "position": part.position,
            "pack_size": part.pack_size,
            "search_score": result["score"],
            "match_type": result["match_type"],
            "matched_field": result["matched_field"],
            "prices": prices,
            "best_price": min(
                prices,
                key=lambda p: p["price"])["price"] if prices else None}
