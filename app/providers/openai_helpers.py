"""
OpenAI Provider Helper Methods

This module contains helper methods for the OpenAI provider implementation.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI


class OpenAIHelpers:
    """Helper methods for OpenAI provider operations."""

    @staticmethod
    async def create_embeddings(client: AsyncOpenAI, texts: List[str], model: str) -> Optional[List[List[float]]]:
        """Create embeddings for a list of texts."""
        try:
            response = await client.embeddings.create(model=model, input=texts)
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return None

    @staticmethod
    async def generate_text(
        client: AsyncOpenAI, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> Optional[str]:
        """Generate text using OpenAI API."""
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating text: {e}")
            return None

    @staticmethod
    async def analyze_query(client: AsyncOpenAI, query: str, model: str) -> Dict[str, Any]:
        """Analyze user query to extract intent and entities."""
        prompt = f"""Analyze this car parts search query and extract:
1. Intent (what the user wants to find)
2. Car brand/model mentioned
3. Part type/category
4. Language (Persian/English)
5. Specific requirements (front/rear, left/right, etc.)

Query: {query}

Respond in JSON format:
{{
    "intent": "search_for_part",
    "car_brand": "Chery",
    "car_model": "Tiggo 8",
    "part_type": "brake_pad",
    "language": "persian",
    "position": "front",
    "specific_requirements": []
}}"""

        try:
            response = await OpenAIHelpers.generate_text(client, prompt, model, 200, 0.1)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Fallback parsing
                    return {
                        "intent": "search",
                        "car_brand": OpenAIHelpers._extract_brand(query),
                        "car_model": OpenAIHelpers._extract_model(query),
                        "part_type": OpenAIHelpers._extract_part_type(query),
                        "language": "persian" if OpenAIHelpers._is_persian(query) else "english",
                        "position": OpenAIHelpers._extract_position(query),
                        "specific_requirements": [],
                    }
            return {"intent": "search", "entities": [], "language": "unknown"}
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return {"intent": "search", "entities": [], "language": "unknown"}

    @staticmethod
    async def generate_suggestions(
        client: AsyncOpenAI, query: str, analysis: Dict[str, Any], results: List[str], model: str
    ) -> List[str]:
        """Generate smart suggestions based on search results."""
        # Extract categories from results
        categories = list(set([result.get("category", "") for result in results if result.get("category")]))
        brands = list(set([result.get("brand_oem", "") for result in results if result.get("brand_oem")]))

        prompt = f"""Based on this car parts search query and results, generate 3 helpful suggestions:

Query: {query}
Found categories: {
            ', '.join(categories)}
Found brands: {
            ', '.join(brands)}

Generate suggestions like:
- Related parts the user might need
- Alternative brands for the same part
- Complementary parts for maintenance

Respond with just 3 suggestions, one per line, in the same language as the query."""

        try:
            response = await OpenAIHelpers.generate_text(client, prompt, model, 150, 0.4)
            if response:
                suggestions = response.strip().split("\n")
                return [s.strip() for s in suggestions if s.strip()][:3]
            return []
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np

            a_np = np.array(a)
            b_np = np.array(b)
            return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))
        except Exception:
            return 0.0

    @staticmethod
    async def check_rate_limits(
        request_times: List[float],
        token_usage: List[tuple],
        requests_per_minute: int,
        tokens_per_minute: int,
    ):
        """Check and enforce rate limits."""
        now = time.time()

        # Clean old request times (older than 1 minute)
        request_times[:] = [t for t in request_times if now - t < 60]
        token_usage[:] = [(t, tokens) for t, tokens in token_usage if now - t < 60]

        # Check request rate limit
        if len(request_times) >= requests_per_minute:
            sleep_time = 60 - (now - request_times[0])
            if sleep_time > 0:
                print(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

        # Check token rate limit
        current_tokens = sum(tokens for _, tokens in token_usage)
        if current_tokens >= tokens_per_minute:
            sleep_time = 60 - (now - token_usage[0][0])
            if sleep_time > 0:
                print(f"Token limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

    @staticmethod
    def _extract_brand(text: str) -> Optional[str]:
        """Extract car brand from text."""
        brands = ["Chery", "JAC", "Brilliance", "BYD", "Geely", "Great Wall", "MG"]
        for brand in brands:
            if brand.lower() in text.lower():
                return brand
        return None

    @staticmethod
    def _extract_model(text: str) -> Optional[str]:
        """Extract car model from text."""
        models = ["Tiggo 8", "X22", "H330", "Arizo 5", "Tiggo 7", "Arrizo 3"]
        for model in models:
            if model.lower() in text.lower():
                return model
        return None

    @staticmethod
    def _extract_part_type(text: str) -> Optional[str]:
        """Extract part type from text."""
        part_types = {
            "brake": ["لنت", "ترمز", "brake", "pad"],
            "filter": ["فیلتر", "filter"],
            "engine": ["موتور", "engine"],
            "suspension": ["تعلیق", "suspension"],
            "transmission": ["گیربکس", "transmission"],
        }

        text_lower = text.lower()
        for part_type, keywords in part_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return part_type
        return None

    @staticmethod
    def _extract_position(text: str) -> Optional[str]:
        """Extract position (front/rear, left/right) from text."""
        positions = ["جلو", "عقب", "چپ", "راست", "front", "rear", "left", "right"]
        text_lower = text.lower()
        for position in positions:
            if position in text_lower:
                return position
        return None

    @staticmethod
    def _is_persian(text: str) -> bool:
        """Check if text contains Persian characters."""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        return bool(persian_pattern.search(text))
