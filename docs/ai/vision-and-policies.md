# AI Vision and Policies

## Executive Summary

This document establishes a comprehensive AI management framework for the China Car Parts system, ensuring controlled, monitored, and cost-effective AI usage across multiple providers with robust fallback mechanisms.

## Strategic Goals

1. **Controlled Traffic**: Every request to AI providers must be monitored, logged, and controlled
2. **Context Management**: Complete visibility and control over data sent to AI services
3. **Response Management**: Full tracking and validation of AI responses
4. **Local Fallback**: Seamless fallback to local processing when AI is unavailable
5. **Multi-Provider Support**: Support for 2+ AI providers with intelligent routing

## Policy Framework

### 1. Rate Limiting and Throttling

#### Global Rate Limits
- **Per User (Telegram ID)**: 20 requests/minute, 200 requests/hour
- **Per IP Address**: 100 requests/minute, 1000 requests/hour
- **Per API Key**: 1000 requests/minute, 10000 requests/hour
- **Burst Allowance**: 50% of limit for 30 seconds

#### Task-Specific Rate Limits
| Task Type | RPM | TPM | Burst | Priority |
|-----------|-----|-----|-------|----------|
| `intelligent_search` | 10 | 500 | 5 | High |
| `semantic_embeddings` | 20 | 1000 | 10 | Medium |
| `query_analysis` | 15 | 300 | 8 | High |
| `suggestion_generation` | 5 | 200 | 3 | Low |
| `bot_quick_reply` | 30 | 100 | 15 | Critical |

### 2. Timeout and Retry Policies

#### Timeout Configuration
- **Primary AI**: 5 seconds timeout, 3 retries with exponential backoff
- **Secondary AI**: 3 seconds timeout, 2 retries with linear backoff
- **Local Fallback**: 1 second timeout, no retries
- **Circuit Breaker**: 5 failures in 60 seconds triggers 30-second cooldown

#### Retry Strategy
```yaml
retry_policy:
  max_attempts: 3
  base_delay: 1.0s
  max_delay: 10.0s
  backoff_multiplier: 2.0
  jitter: true
  retryable_errors: [timeout, rate_limit, service_unavailable]
```

### 3. Budget and Cost Management

#### Monthly Budget Limits
- **OpenAI**: $500/month hard limit
- **Alternative Provider**: $300/month hard limit
- **Total AI Budget**: $800/month with 10% buffer
- **Emergency Override**: Admin can increase by 50% for 24 hours

#### Cost Controls
- **Per-Request Cost**: Maximum $0.10 per request
- **Daily Spending Alert**: 80% of daily budget
- **Auto-Shutdown**: 95% of monthly budget triggers read-only mode
- **Cost Tracking**: Real-time token usage and cost calculation

### 4. Model and Provider Management

#### Approved Models
```yaml
providers:
  openai:
    models:
      - gpt-3.5-turbo (chat, analysis)
      - gpt-4 (premium analysis)
      - text-embedding-3-small (embeddings)
    max_tokens: 2000
    temperature_range: [0.0, 0.7]
  
  anthropic:
    models:
      - claude-3-haiku (fast responses)
      - claude-3-sonnet (balanced)
    max_tokens: 1500
    temperature_range: [0.0, 0.5]
  
  local:
    models:
      - sentence-transformers (embeddings)
      - rule-based (fallback)
    max_tokens: 1000
    temperature_range: [0.0, 0.3]
```

#### Routing Rules
1. **Primary Route**: OpenAI for all tasks
2. **Secondary Route**: Anthropic for chat/analysis tasks
3. **Fallback Route**: Local processing for all tasks
4. **Load Balancing**: 70% OpenAI, 30% Anthropic during normal operation

### 5. Data Privacy and PII Protection

#### Input Sanitization
- **PII Detection**: Regex patterns for phone numbers, emails, names
- **Data Masking**: Replace PII with placeholders before AI calls
- **Sanitization Log**: Track what was masked and why
- **User Consent**: Explicit consent for data processing

#### Output Validation
- **Response Filtering**: Remove any PII from AI responses
- **Content Validation**: Check for inappropriate or off-topic content
- **Quality Scoring**: Rate response relevance and accuracy
- **Audit Trail**: Complete log of all data transformations

#### Data Retention
- **Prompt Data**: 30 days maximum
- **Response Data**: 90 days maximum
- **Logs**: 1 year for security, 30 days for performance
- **Anonymized Analytics**: Indefinite for improvement

### 6. Task-Specific Policies

#### Intelligent Search
```yaml
intelligent_search:
  max_tokens: 1000
  temperature: 0.3
  timeout: 5s
  retries: 3
  fallback: basic_search
  cost_limit: $0.05
  quality_threshold: 0.7
```

#### Semantic Embeddings
```yaml
semantic_embeddings:
  max_tokens: 500
  temperature: 0.0
  timeout: 3s
  retries: 2
  fallback: fuzzy_search
  cost_limit: $0.02
  batch_size: 10
```

#### Query Analysis
```yaml
query_analysis:
  max_tokens: 200
  temperature: 0.1
  timeout: 2s
  retries: 2
  fallback: rule_based_analysis
  cost_limit: $0.01
  response_format: json
```

#### Bot Quick Reply
```yaml
bot_quick_reply:
  max_tokens: 150
  temperature: 0.2
  timeout: 1s
  retries: 1
  fallback: predefined_responses
  cost_limit: $0.005
  response_language: persian
```

### 7. Observability and Monitoring

#### Logging Requirements
```yaml
logging:
  level: INFO
  format: json
  fields:
    - timestamp
    - request_id
    - user_id
    - task_type
    - provider
    - model
    - input_tokens
    - output_tokens
    - cost
    - latency
    - success
    - error_code
    - masked_prompt
    - sanitized_response
```

#### Metrics Collection
- **Performance**: P95 latency, throughput, error rate
- **Cost**: Token usage, cost per request, daily/monthly spend
- **Quality**: Response relevance score, user satisfaction
- **Reliability**: Uptime, fallback usage, circuit breaker trips

#### Alerting Rules
- **Critical**: AI service down, budget exceeded, security breach
- **Warning**: High error rate, slow response, approaching budget limit
- **Info**: New user patterns, model performance changes

### 8. Fallback and Local Processing

#### Fallback Hierarchy
1. **Primary AI** (OpenAI) → **Secondary AI** (Anthropic) → **Local Processing**
2. **Local Processing Options**:
   - Rule-based search algorithms
   - Pre-computed similarity matrices
   - Cached responses
   - Basic fuzzy matching

#### Local Processing Capabilities
- **Embeddings**: Sentence-transformers models
- **Search**: Elasticsearch with custom scoring
- **Analysis**: Regex-based entity extraction
- **Suggestions**: Pre-defined response templates

#### Fallback SLAs
- **Response Time**: < 2 seconds for local fallback
- **Availability**: 99.9% uptime for local processing
- **Quality**: 80% of AI response quality
- **Coverage**: 90% of AI functionality

### 9. Policy Configuration Schema

#### Policy Configuration Format
```yaml
# /config/ai-policies.yaml
version: "1.0"
last_updated: "2024-01-15T00:00:00Z"

global:
  budget:
    monthly_limit: 800
    daily_limit: 26.67
    emergency_buffer: 0.1
  
  rate_limits:
    per_user_rpm: 20
    per_ip_rpm: 100
    burst_multiplier: 1.5
  
  timeouts:
    primary: 5s
    secondary: 3s
    fallback: 1s

providers:
  openai:
    enabled: true
    priority: 1
    api_key: "${OPENAI_API_KEY}"
    models:
      gpt-3.5-turbo:
        max_tokens: 2000
        temperature: 0.3
        cost_per_1k_tokens: 0.002
  
  anthropic:
    enabled: true
    priority: 2
    api_key: "${ANTHROPIC_API_KEY}"
    models:
      claude-3-haiku:
        max_tokens: 1500
        temperature: 0.2
        cost_per_1k_tokens: 0.001

tasks:
  intelligent_search:
    providers: [openai, anthropic, local]
    timeout: 5s
    retries: 3
    cost_limit: 0.05
    quality_threshold: 0.7
  
  semantic_embeddings:
    providers: [openai, local]
    timeout: 3s
    retries: 2
    cost_limit: 0.02
    batch_size: 10

privacy:
  pii_detection: true
  data_masking: true
  retention_days: 30
  audit_logging: true

monitoring:
  log_level: INFO
  metrics_retention: 90d
  alerting_enabled: true
  dashboard_url: "https://monitoring.example.com/ai"
```

### 10. Implementation Phases

#### Phase 1: Foundation (Weeks 1-2)
- Implement rate limiting and basic monitoring
- Add PII detection and masking
- Create policy configuration system
- Set up basic fallback mechanisms

#### Phase 2: Multi-Provider (Weeks 3-4)
- Integrate secondary AI provider
- Implement intelligent routing
- Add cost tracking and budget controls
- Create admin panel for policy management

#### Phase 3: Advanced Features (Weeks 5-6)
- Implement local processing capabilities
- Add quality scoring and validation
- Create comprehensive monitoring dashboard
- Implement advanced fallback strategies

#### Phase 4: Optimization (Weeks 7-8)
- Performance tuning and optimization
- A/B testing for different configurations
- Advanced analytics and reporting
- Continuous improvement based on usage patterns

## Clarifying Questions

1. **Budget and Cost Management**: What is the preferred monthly budget allocation between different AI providers, and should we implement per-tenant or per-user budget limits for multi-tenant scenarios?

2. **Data Retention and Privacy**: What are the specific compliance requirements for data retention (GDPR, CCPA, etc.), and what level of PII masking is acceptable (full anonymization vs. partial masking)?

3. **Policy Management and Access Control**: Who should have the authority to modify AI policies (admin-only vs. role-based), and should there be approval workflows for policy changes?

4. **Quality and Performance Standards**: What are the acceptable quality thresholds for AI responses, and what should be the target response times for different task types?

5. **Fallback and Local Processing**: What level of functionality should the local fallback system provide, and are there specific local models or processing libraries you prefer?

6. **Monitoring and Alerting**: What are the critical metrics that require real-time alerting, and who should receive these alerts (technical team, business stakeholders, or both)?

7. **Multi-Provider Strategy**: Should we implement load balancing between providers, or use them as strict failover options? Are there specific providers beyond OpenAI and Anthropic that should be considered?
