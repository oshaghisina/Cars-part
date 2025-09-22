# AI Current State Documentation

## Overview

This document maps the current AI implementation in the China Car Parts system, including touchpoints, configurations, data flows, and identified gaps.

## AI Touchpoints Inventory

### Core AI Service
**File**: `app/services/ai_service.py` (Lines 1-475)
- **Class**: `AIService`
- **Purpose**: Central AI service for semantic search and intelligent query processing
- **Dependencies**: OpenAI API, NumPy, SQLAlchemy

### Configuration Management
**File**: `app/core/config.py` (Lines 23-33)
- **AI Settings**:
  - `ai_enabled: bool = True` - Master toggle
  - `openai_api_key: Optional[str] = None` - API authentication
  - `openai_model: str = "gpt-3.5-turbo"` - Chat completion model
  - `openai_embedding_model: str = "text-embedding-3-small"` - Embedding model
  - `openai_max_tokens: int = 1000` - Response limit
  - `openai_temperature: float = 0.3` - Response creativity

### Service Integration Points

#### Bot Service Integration
**File**: `app/services/bot_service.py` (Lines 35-42)
- **Function**: `search_and_confirm_part()`
- **AI Usage**: Calls `ai_service.intelligent_search()` with fallback to basic search
- **Error Handling**: Catches AI exceptions and falls back gracefully

#### Search Service Integration
**File**: `app/services/search.py` (Lines 34-45)
- **Function**: `search_parts()`
- **AI Usage**: Calls `ai_service.semantic_search()` when AI enabled
- **Fallback**: Falls back to basic/fuzzy search on AI failure

### API Router Integration
**File**: `app/api/routers/search.py` (Lines 21-91)
- **Endpoints**: `/search/advanced`, `/search/global`
- **AI Usage**: Indirect through SearchService
- **Note**: No direct AI calls in API layer

### Bot Handler Integration
**File**: `app/bot/bot.py` (Lines 156, 434-471)
- **AI Command**: `/ai` command for AI settings toggle
- **Search Flow**: Uses BotService which integrates AI
- **User Experience**: AI failures are transparent to users

### Admin Panel Integration
**File**: `app/frontend/panel/src/views/Settings.vue` (Lines 16-33, 139-162)
- **AI Toggle**: Checkbox to enable/disable AI search
- **API Endpoint**: `PUT /api/v1/admin/settings` for AI_ENABLED
- **UI State**: `aiEnabled` reactive variable

## Models and Providers

### OpenAI Integration
- **Provider**: OpenAI API
- **Models Used**:
  - `gpt-3.5-turbo` for chat completions (query analysis, expansion, suggestions)
  - `text-embedding-3-small` for semantic embeddings
- **API Key**: Stored in `openai_api_key` environment variable
- **Rate Limits**: No explicit rate limiting implemented
- **Cost Model**: Pay-per-token usage

### Embedding Strategy
- **Input**: Part descriptions concatenated from multiple fields
- **Format**: `"{part_name} {brand_oem} {vehicle_make} {vehicle_model} {category} {oem_code} {vehicle_trim} {position}"`
- **Similarity**: Cosine similarity with 0.7 threshold
- **Batch Processing**: Single API call for all parts

## Call Shapes and Payloads

### Semantic Search
- **Input**: Query string + limit
- **Process**: Create embeddings for query and all parts, calculate similarities
- **Output**: Ranked list of parts with similarity scores
- **Payload Size**: Variable based on parts database size

### Intelligent Search
- **Input**: Query string + limit
- **Process**: 
  1. Query analysis (JSON extraction)
  2. Query expansion (3 alternative queries)
  3. Multiple semantic searches
  4. Suggestion generation
- **Output**: Enhanced results with analysis and suggestions
- **Payload Size**: Multiple API calls per search

### Query Analysis
- **Input**: User query string
- **Prompt**: Structured JSON extraction for intent, entities, language
- **Output**: Parsed analysis with fallback parsing
- **Token Usage**: ~200 tokens per analysis

### Query Expansion
- **Input**: Original query + analysis
- **Prompt**: Generate 3 alternative search queries
- **Output**: List of expanded queries
- **Token Usage**: ~150 tokens per expansion

### Suggestion Generation
- **Input**: Query + analysis + search results
- **Prompt**: Generate 3 helpful suggestions
- **Output**: List of suggestions
- **Token Usage**: ~150 tokens per suggestion

## Data Flow

### Input Data
- **User Queries**: Persian/English text from Telegram bot
- **Part Database**: All active parts with descriptions
- **Search Context**: Query analysis and expansion

### Processing Flow
1. **Query Reception** → Bot Service → AI Service
2. **Availability Check** → `is_available()` method
3. **Query Analysis** → OpenAI chat completion
4. **Query Expansion** → Generate alternatives
5. **Semantic Search** → Embedding creation and similarity
6. **Suggestion Generation** → Context-aware recommendations
7. **Result Formatting** → Standardized response format

### Output Data
- **Search Results**: Ranked parts with scores
- **Query Analysis**: Intent, entities, language detection
- **Suggestions**: Related parts and alternatives
- **Error Handling**: Graceful fallback to basic search

## Toggles and Flags

### Master Controls
- **`ai_enabled`**: Global AI on/off switch (environment variable)
- **`openai_api_key`**: API key presence determines availability
- **Admin Panel Toggle**: Runtime AI enable/disable via UI

### Feature Flags
- **Similarity Threshold**: 0.7 minimum for semantic matches
- **Query Expansion Limit**: 3 alternative queries maximum
- **Suggestion Limit**: 3 suggestions per search
- **Bulk Search Limit**: Configurable via `bulk_limit_default`

## Error Handling and Fallbacks

### AI Service Unavailable
- **Detection**: `is_available()` checks client and settings
- **Fallback**: Automatic fallback to `SearchService.search_parts()`
- **User Impact**: Transparent - users don't see AI failure

### API Errors
- **OpenAI API Errors**: Caught and logged, fallback to basic search
- **Embedding Failures**: Logged with warning, fallback to basic search
- **JSON Parsing Errors**: Fallback parsing with regex extraction

### Graceful Degradation
- **Search Service**: Always falls back to basic/fuzzy search
- **Bot Service**: Always provides search results regardless of AI status
- **User Experience**: No error messages for AI failures

## Identified Gaps and Risks

### Security and Privacy
- **PII Exposure**: User queries sent to OpenAI (no sanitization)
- **API Key Security**: Stored in environment variables (good)
- **Data Retention**: No control over OpenAI data retention

### Performance and Cost
- **No Rate Limiting**: No explicit OpenAI API rate limiting
- **No Caching**: Embeddings recalculated on every search
- **No Budget Controls**: No cost monitoring or limits
- **Batch Inefficiency**: Single API call for all parts (scales poorly)

### Reliability
- **Single Point of Failure**: OpenAI API dependency
- **No Retry Logic**: Single attempt per API call
- **No Circuit Breaker**: No protection against API failures
- **No Health Checks**: No monitoring of AI service health

### Data Quality
- **No Validation**: No validation of AI-generated suggestions
- **No Quality Metrics**: No tracking of AI result quality
- **No Learning**: No feedback loop for improvement
- **No A/B Testing**: No comparison of AI vs basic search

### Monitoring and Observability
- **Limited Logging**: Basic error logging only
- **No Metrics**: No AI usage or performance metrics
- **No Alerts**: No alerting for AI failures
- **No Analytics**: No tracking of AI effectiveness

### Scalability
- **Database Growth**: Embedding calculation scales with parts count
- **Memory Usage**: All parts loaded into memory for embedding
- **Concurrent Users**: No consideration for concurrent AI usage
- **Resource Limits**: No resource usage monitoring

## Recommendations for Improvement

### Immediate (High Priority)
1. **Implement API Rate Limiting**: Add OpenAI rate limiting and retry logic
2. **Add Cost Monitoring**: Track API usage and costs
3. **Implement Caching**: Cache embeddings and search results
4. **Add Health Checks**: Monitor AI service availability

### Medium Term
1. **Add PII Sanitization**: Remove sensitive data before API calls
2. **Implement Circuit Breaker**: Protect against API failures
3. **Add Quality Metrics**: Track AI result effectiveness
4. **Implement A/B Testing**: Compare AI vs basic search performance

### Long Term
1. **Consider Local Models**: Evaluate local embedding models
2. **Add Learning Loop**: Implement feedback-based improvement
3. **Add Advanced Analytics**: Comprehensive AI usage analytics
4. **Implement Budget Controls**: Hard limits on API usage

## Questions for Clarification

1. **Cost Management**: What is the expected monthly budget for OpenAI API usage, and should we implement hard cost limits?

2. **Data Privacy**: Are there any specific PII concerns with sending user queries to OpenAI, and should we implement query sanitization?

3. **Performance Requirements**: What are the acceptable response times for AI-enhanced search, and should we implement caching strategies?

4. **Quality Assurance**: How should we measure and ensure the quality of AI-generated suggestions and search results?

5. **Scalability Planning**: What is the expected growth in parts database size, and should we consider local embedding models for better scalability?

6. **Monitoring and Alerting**: What level of AI service monitoring is required, and should we implement real-time alerting for AI failures?

7. **Fallback Strategy**: Should the fallback to basic search be completely transparent to users, or should there be some indication when AI is unavailable?
