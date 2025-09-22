"""
OpenAI Provider Implementation

This module implements the OpenAI provider for the AI Gateway system.
It provides real OpenAI API integration with proper error handling,
rate limiting, and cost estimation.
"""

from typing import Any, Dict, List

from openai import AsyncOpenAI

from app.services.ai_provider import AIProvider, AIResponse, TaskType


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation with real API integration."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.default_model = config.get("default_model", "gpt-3.5-turbo")
        self.embedding_model = config.get("embedding_model", "text-embedding-3-small")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.3)
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)

        # Rate limiting
        self.requests_per_minute = config.get("requests_per_minute", 60)
        self.tokens_per_minute = config.get("tokens_per_minute", 40000)
        self._request_times = []
        self._token_usage = []

        # Cost tracking (approximate costs as of 2024)
        self.cost_per_1k_tokens = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
        }

        # Initialize OpenAI client
        self._client = None
        self._initialize_client()

        # Supported capabilities
        self._capabilities = [
            TaskType.SEMANTIC_SEARCH,
            TaskType.INTELLIGENT_SEARCH,
            TaskType.QUERY_ANALYSIS,
            TaskType.SUGGESTION_GENERATION,
            TaskType.PART_RECOMMENDATIONS,
        ]

    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            if not self.api_key:
                print(f"OpenAI API key not provided for provider '{self.name}'")
                self._update_status(self._get_status_enum().UNHEALTHY)
                return

            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            print(f"OpenAI client initialized for provider '{self.name}'")
            self._update_status(self._get_status_enum().HEALTHY)
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            self._update_status(self._get_status_enum().UNHEALTHY)

    def _get_status_enum(self):
        """Get the ProviderStatus enum."""
        from app.services.ai_provider import ProviderStatus

        return ProviderStatus

    async def execute_task(self, task_type: TaskType,
                           context: Dict[str, Any], **kwargs) -> AIResponse:
        """
        Execute an AI task using OpenAI APIs.

        Args:
            task_type: Type of AI task to execute
            context: Context data for the task
            **kwargs: Additional task-specific parameters

        Returns:
            AIResponse: Standardized response
        """
        if not self.is_available():
            return AIResponse(
                content=None,
                metadata={"error": "Provider not available"},
                provider=self.name,
                task_type=task_type,
            )

        try:
            # Check rate limits
            await self._check_rate_limits()

            if task_type == TaskType.SEMANTIC_SEARCH:
                return await self._execute_semantic_search(context, **kwargs)
            elif task_type == TaskType.INTELLIGENT_SEARCH:
                return await self._execute_intelligent_search(context, **kwargs)
            elif task_type == TaskType.QUERY_ANALYSIS:
                return await self._execute_query_analysis(context, **kwargs)
            elif task_type == TaskType.SUGGESTION_GENERATION:
                return await self._execute_suggestion_generation(context, **kwargs)
            elif task_type == TaskType.PART_RECOMMENDATIONS:
                return await self._execute_part_recommendations(context, **kwargs)
            else:
                return AIResponse(
                    content=None,
                    metadata={"error": f"Unsupported task type: {task_type}"},
                    provider=self.name,
                    task_type=task_type,
                )

        except Exception as e:
            self._handle_error(e)
            return AIResponse(
                content=None,
                metadata={"error": str(e)},
                provider=self.name,
                task_type=task_type,
            )

    def is_available(self) -> bool:
        """Check if the provider is available and healthy."""
        return self._client is not None and self.is_healthy()

    def get_capabilities(self) -> List[TaskType]:
        """Get list of task types this provider supports."""
        return self._capabilities.copy()

    def estimate_cost(self, task_type: TaskType, context: Dict[str, Any]) -> float:
        """Estimate cost for a task before execution."""
        # Rough estimation based on context size and task type
        if task_type == TaskType.SEMANTIC_SEARCH:
            query = context.get("query", "")
            parts = context.get("parts", [])
            estimated_tokens = len(query.split()) * 2 + len(parts) * 50  # Rough estimate
            return self._calculate_cost(self.embedding_model, estimated_tokens, True)
        elif task_type in [
            TaskType.INTELLIGENT_SEARCH,
            TaskType.QUERY_ANALYSIS,
            TaskType.SUGGESTION_GENERATION,
        ]:
            query = context.get("query", "")
            estimated_tokens = len(query.split()) * 4  # Rough estimate
            return self._calculate_cost(self.default_model, estimated_tokens, True)
        else:
            return 0.0

    def _calculate_cost(self, model: str, tokens: int, is_input: bool) -> float:
        """Calculate cost for a specific model and token count."""
        if model not in self.cost_per_1k_tokens:
            return 0.0

        cost_per_1k = self.cost_per_1k_tokens[model]["input" if is_input else "output"]
        return (tokens / 1000) * cost_per_1k

    async def _check_rate_limits(self):
        """Check and enforce rate limits."""
        from app.providers.openai_helpers import OpenAIHelpers

        await OpenAIHelpers.check_rate_limits(
            self._request_times, self._token_usage, self.requests_per_minute, self.tokens_per_minute
        )

    async def _execute_semantic_search(self, context: Dict[str, Any], **kwargs) -> AIResponse:
        """Execute semantic search using embeddings."""
        from app.providers.openai_helpers import OpenAIHelpers

        query = context.get("query", "")
        parts = context.get("parts", [])
        limit = kwargs.get("limit", 10)

        if not query or not parts:
            return AIResponse(
                content=[],
                metadata={"error": "Missing query or parts data"},
                provider=self.name,
                task_type=TaskType.SEMANTIC_SEARCH,
            )

        try:
            # Create embeddings for query and parts
            if not self._client:
                return AIResponse(
                    content=[],
                    metadata={"error": "OpenAI client not initialized"},
                    provider=self.name,
                    task_type=TaskType.SEMANTIC_SEARCH,
                )

            query_embedding = await OpenAIHelpers.create_embeddings(self._client, [query], self.embedding_model)
            if not query_embedding:
                return AIResponse(
                    content=[],
                    metadata={"error": "Failed to create query embedding"},
                    provider=self.name,
                    task_type=TaskType.SEMANTIC_SEARCH,
                )

            # Create embeddings for all parts
            part_texts = []
            for part in parts:
                text = f"{
                    part.get(
                        'part_name',
                        '')} {
                    part.get(
                        'brand_oem',
                        '')} {
                    part.get(
                        'vehicle_make',
                        '')} {
                            part.get(
                                'vehicle_model',
                                '')} {
                                    part.get(
                                        'category',
                                        '')}"
                part_texts.append(text)

            part_embeddings = await OpenAIHelpers.create_embeddings(self._client, part_texts, self.embedding_model)
            if not part_embeddings:
                return AIResponse(
                    content=[],
                    metadata={"error": "Failed to create part embeddings"},
                    provider=self.name,
                    task_type=TaskType.SEMANTIC_SEARCH,
                )

            # Calculate similarities
            similarities = []
            for i, part_embedding in enumerate(part_embeddings):
                similarity = OpenAIHelpers.cosine_similarity(query_embedding[0], part_embedding)
                if similarity > 0.7:  # Minimum similarity threshold
                    result = parts[i].copy()
                    result["search_score"] = similarity
                    result["match_type"] = "semantic"
                    result["matched_field"] = "ai_similarity"
                    similarities.append(result)

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["search_score"], reverse=True)
            results = similarities[:limit]

            self._handle_success()
            return AIResponse(
                content=results,
                metadata={
                    "query": query,
                    "total_parts": len(parts),
                    "matched_parts": len(results),
                    "similarity_threshold": 0.7,
                },
                provider=self.name,
                task_type=TaskType.SEMANTIC_SEARCH,
            )

        except Exception as e:
            self._handle_error(e)
            raise

    async def _execute_intelligent_search(self, context: Dict[str, Any], **kwargs) -> AIResponse:
        """Execute intelligent search with query understanding and expansion."""
        from app.providers.openai_helpers import OpenAIHelpers

        query = context.get("query", "")

        if not query:
            return AIResponse(
                content={"success": False, "parts": [], "error": "No query provided"},
                metadata={"error": "Missing query"},
                provider=self.name,
                task_type=TaskType.INTELLIGENT_SEARCH,
            )

        try:
            # Analyze the query
            if not self._client:
                return AIResponse(
                    content={
                        "success": False,
                        "parts": [],
                        "error": "OpenAI client not initialized",
                    },
                    metadata={"error": "OpenAI client not initialized"},
                    provider=self.name,
                    task_type=TaskType.INTELLIGENT_SEARCH,
                )

            analysis = await OpenAIHelpers.analyze_query(self._client, query, self.default_model)

            # Generate suggestions
            suggestions = await OpenAIHelpers.generate_suggestions(
                self._client, query, analysis, [], self.default_model
            )

            # For now, return analysis and suggestions (semantic search would be called separately)
            result = {
                "success": True,
                "parts": [],  # Would be populated by semantic search
                "query_analysis": analysis,
                "suggestions": suggestions,
                "search_type": "intelligent",
            }

            self._handle_success()
            return AIResponse(
                content=result,
                metadata={
                    "query": query,
                    "analysis": analysis,
                    "suggestions_count": len(suggestions),
                },
                provider=self.name,
                task_type=TaskType.INTELLIGENT_SEARCH,
            )

        except Exception as e:
            self._handle_error(e)
            raise

    async def _execute_query_analysis(self, context: Dict[str, Any], **kwargs) -> AIResponse:
        """Execute query analysis to extract intent and entities."""
        from app.providers.openai_helpers import OpenAIHelpers

        query = context.get("query", "")

        if not query:
            return AIResponse(
                content=None,
                metadata={"error": "No query provided"},
                provider=self.name,
                task_type=TaskType.QUERY_ANALYSIS,
            )

        try:
            if not self._client:
                return AIResponse(
                    content=None,
                    metadata={"error": "OpenAI client not initialized"},
                    provider=self.name,
                    task_type=TaskType.QUERY_ANALYSIS,
                )

            analysis = await OpenAIHelpers.analyze_query(self._client, query, self.default_model)

            self._handle_success()
            return AIResponse(
                content=analysis,
                metadata={"query": query, "analysis_type": "intent_extraction"},
                provider=self.name,
                task_type=TaskType.QUERY_ANALYSIS,
            )

        except Exception as e:
            self._handle_error(e)
            raise

    async def _execute_suggestion_generation(self, context: Dict[str, Any], **kwargs) -> AIResponse:
        """Execute suggestion generation."""
        from app.providers.openai_helpers import OpenAIHelpers

        query = context.get("query", "")
        analysis = context.get("analysis", {})
        results = context.get("results", [])

        if not query:
            return AIResponse(
                content=[],
                metadata={"error": "No query provided"},
                provider=self.name,
                task_type=TaskType.SUGGESTION_GENERATION,
            )

        try:
            if not self._client:
                return AIResponse(
                    content=[],
                    metadata={"error": "OpenAI client not initialized"},
                    provider=self.name,
                    task_type=TaskType.SUGGESTION_GENERATION,
                )

            suggestions = await OpenAIHelpers.generate_suggestions(
                self._client, query, analysis, results, self.default_model
            )

            self._handle_success()
            return AIResponse(
                content=suggestions,
                metadata={
                    "query": query,
                    "analysis": analysis,
                    "results_count": len(results),
                    "suggestions_count": len(suggestions),
                },
                provider=self.name,
                task_type=TaskType.SUGGESTION_GENERATION,
            )

        except Exception as e:
            self._handle_error(e)
            raise

    async def _execute_part_recommendations(self, context: Dict[str, Any], **kwargs) -> AIResponse:
        """Execute part recommendations based on a specific part."""
        from app.providers.openai_helpers import OpenAIHelpers

        part_id = context.get("part_id")
        part_data = context.get("part_data", {})
        limit = kwargs.get("limit", 5)

        if not part_id and not part_data:
            return AIResponse(
                content=[],
                metadata={"error": "No part data provided"},
                provider=self.name,
                task_type=TaskType.PART_RECOMMENDATIONS,
            )

        try:
            # Create part description for similarity search
            part_description = (
                f"{part_data.get('part_name', '')} {part_data.get('brand_oem', '')} "
                f"{part_data.get('vehicle_make', '')} {part_data.get('vehicle_model', '')} "
                f"{part_data.get('category', '')}"
            )

            # Generate recommendations using text generation
            prompt = f"""Based on this car part: {part_description}

Generate 3-5 related car parts that customers might also need:
1. Complementary parts (parts that work together)
2. Alternative brands for the same part
3. Maintenance parts for the same vehicle

Return only the part names, one per line:"""

            if not self._client:
                return AIResponse(
                    content=[],
                    metadata={"error": "OpenAI client not initialized"},
                    provider=self.name,
                    task_type=TaskType.PART_RECOMMENDATIONS,
                )

            response = await OpenAIHelpers.generate_text(self._client, prompt, self.default_model, 200, 0.5)

            recommendations = []
            if response:
                lines = response.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(("1.", "2.", "3.", "4.", "5.")):
                        recommendations.append(line)

            self._handle_success()
            return AIResponse(
                content=recommendations[:limit],
                metadata={
                    "part_id": part_id,
                    "part_description": part_description,
                    "recommendations_count": len(recommendations),
                },
                provider=self.name,
                task_type=TaskType.PART_RECOMMENDATIONS,
            )

        except Exception as e:
            self._handle_error(e)
            raise
