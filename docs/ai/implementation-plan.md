# AI Gateway Implementation Plan

## 1. Epics & Work Breakdown (Incremental)

### E1: Foundation - AI Provider Interface & Client Skeleton
**Duration**: 2-3 weeks
**Goal**: Establish core interfaces and basic OpenAI provider with monitoring hooks

**Work Items**:
- **AIProvider Interface**: Abstract base class with `execute_task()`, `is_available()`, `get_capabilities()`
- **AIClient Skeleton**: Unified client with timeout/retry/circuit breaker hooks
- **OpenAI Provider**: First concrete implementation with existing OpenAI integration
- **Masked Logging**: Request/response logging with PII redaction
- **Configuration**: Environment variables for provider settings

**Deliverables**:
- `app/services/ai_provider.py` - Base provider interface
- `app/services/ai_client.py` - Unified client with policy hooks
- `app/providers/openai_provider.py` - OpenAI implementation
- `app/services/ai_logging.py` - Masked logging utilities

### E2: Orchestrator - Policy-Driven Routing
**Duration**: 3-4 weeks
**Goal**: Central orchestration with configurable routing and feature flags

**Work Items**:
- **AIOrchestrator**: Central coordination class with policy enforcement
- **Policy Engine**: Rate limiting, budget controls, routing decisions
- **Task Entrypoints**: `semantic_search()`, `intelligent_search()`, `get_recommendations()`
- **Feature Flags**: Runtime toggles for AI functionality
- **Configuration Management**: Database-driven policy configuration

**Deliverables**:
- `app/services/ai_orchestrator.py` - Main orchestration logic
- `app/services/ai_policy_engine.py` - Policy enforcement
- `app/models/ai_config.py` - Configuration models
- Database migrations for AI configuration tables

### E3: Context & Normalization
**Duration**: 2-3 weeks
**Goal**: Context management and response standardization

**Work Items**:
- **ContextBuilder**: Prompt templates, PII redaction, token budgeting
- **Normalizer**: Response schema validation, metadata extraction
- **Template Management**: Versioned prompt templates with variables
- **Token Management**: Cost calculation and budget enforcement
- **PII Detection**: Automated detection and masking of sensitive data

**Deliverables**:
- `app/services/ai_context.py` - Context building and sanitization
- `app/services/ai_normalizer.py` - Response normalization
- `app/templates/ai_prompts/` - Prompt template directory
- `app/utils/pii_detector.py` - PII detection utilities

### E4: Fallbacks - Local Processing
**Duration**: 2-3 weeks
**Goal**: Robust fallback mechanisms when AI providers fail

**Work Items**:
- **Local Heuristics**: RapidFuzz-based fuzzy search and synonym matching
- **Local Embeddings**: Optional sentence-transformers integration
- **Fallback Orchestration**: Configurable fallback order and conditions
- **Circuit Breaker**: Automatic failover and recovery
- **Performance Optimization**: Caching and response time optimization

**Deliverables**:
- `app/services/ai_fallbacks.py` - Fallback orchestration
- `app/fallbacks/local_search.py` - Local fuzzy search
- `app/fallbacks/local_embeddings.py` - Local embeddings (optional)
- `app/services/circuit_breaker.py` - Circuit breaker implementation

### E5: Wire-Up - Integration Points
**Duration**: 2-3 weeks
**Goal**: Minimal integration with existing services while preserving APIs

**Work Items**:
- **SearchService Integration**: Route through orchestrator when AI enabled
- **BotService Integration**: Maintain existing bot UX with new backend
- **API Router Integration**: Preserve existing REST endpoints
- **Feature Flag Gating**: `ai_enabled` check in gateway
- **Backward Compatibility**: Ensure existing functionality unchanged

**Deliverables**:
- Updated `app/services/search.py` - Orchestrator integration
- Updated `app/services/bot_service.py` - Gateway routing
- Updated `app/api/routers/search.py` - Preserved API contracts
- Integration tests for all touchpoints

### E6: Observability - Traces & Metrics
**Duration**: 2-3 weeks
**Goal**: Comprehensive monitoring and debugging capabilities

**Work Items**:
- **Request Tracing**: End-to-end request correlation with request_id
- **Metrics Collection**: Performance, cost, and error metrics
- **Log Aggregation**: Structured logging with correlation IDs
- **Read-Only Endpoints**: Traces and metrics API endpoints
- **Dashboard Data**: Real-time metrics for admin panel

**Deliverables**:
- `app/services/ai_tracing.py` - Request tracing utilities
- `app/services/ai_metrics.py` - Metrics collection
- `app/api/routers/ai_observability.py` - Read-only endpoints
- `app/models/ai_trace.py` - Trace data models

### E7: Admin Panel (Phase 1) - Read-Only Interface
**Duration**: 3-4 weeks
**Goal**: Basic admin interface for monitoring and configuration

**Work Items**:
- **Provider Status**: Health checks and configuration display
- **Policy Viewing**: Current policy configuration (read-only)
- **Trace Browser**: Search and view request traces (masked)
- **Feature Flag Management**: Toggle AI functionality
- **Metrics Dashboard**: Real-time performance and cost metrics

**Deliverables**:
- `app/frontend/panel/src/views/AI/` - Admin panel pages
- `app/api/routers/ai_admin.py` - Admin API endpoints
- `app/components/AI/` - Reusable AI admin components
- Integration with existing admin panel

### E8: Testing - Comprehensive Test Suite
**Duration**: 2-3 weeks
**Goal**: Robust testing strategy with failure simulation

**Work Items**:
- **Unit Tests**: Provider interfaces, orchestrator logic, policy engine
- **Integration Tests**: End-to-end workflows with real providers
- **Stub Provider**: Mock provider for testing without external dependencies
- **Chaos Testing**: Provider failures, timeouts, rate limiting
- **Load Testing**: Performance validation and bottleneck identification

**Deliverables**:
- `tests/unit/ai/` - Unit test suite
- `tests/integration/ai/` - Integration tests
- `app/providers/stub_provider.py` - Mock provider
- `tests/chaos/ai/` - Failure simulation tests
- Load testing scripts and targets

### E9: Rollout & Backout - Production Deployment
**Duration**: 2-3 weeks
**Goal**: Safe production rollout with rollback capabilities

**Work Items**:
- **Canary Deployment**: Gradual traffic migration (10% → 50% → 100%)
- **Kill Switch**: Emergency disable mechanism
- **Hot Reload**: Runtime configuration updates
- **Backout Plan**: Quick revert to existing AI service
- **Monitoring**: Real-time health checks and alerting

**Deliverables**:
- Deployment scripts with canary controls
- Emergency rollback procedures
- Configuration hot-reload implementation
- Production monitoring and alerting
- Rollout documentation and runbooks

## 2. Milestones & Acceptance Criteria

### Milestone 1: Foundation Complete (E1)
**Acceptance Criteria**:
- [ ] AIProvider interface implemented and tested
- [ ] OpenAI provider working with existing functionality
- [ ] Masked logging capturing all AI requests
- [ ] Configuration system operational
- [ ] No performance regression in existing AI calls

### Milestone 2: Orchestration Ready (E2)
**Acceptance Criteria**:
- [ ] Policy engine enforcing rate limits and budgets
- [ ] Task entrypoints routing through orchestrator
- [ ] Feature flags controlling AI functionality
- [ ] Database configuration system operational
- [ ] Gateway adds ≤50ms p95 latency overhead

### Milestone 3: Context & Fallbacks (E3-E4)
**Acceptance Criteria**:
- [ ] PII redaction working on all outgoing data
- [ ] Local fallbacks providing 99% success rate when AI is down
- [ ] Response normalization maintaining data quality
- [ ] Circuit breaker preventing cascade failures
- [ ] Token budgeting preventing cost overruns

### Milestone 4: Integration Complete (E5)
**Acceptance Criteria**:
- [ ] All existing AI touchpoints using orchestrator
- [ ] Public APIs unchanged and backward compatible
- [ ] Bot UX preserved with new backend
- [ ] Feature flag gating working correctly
- [ ] Integration tests passing

### Milestone 5: Observability & Admin (E6-E7)
**Acceptance Criteria**:
- [ ] Request tracing working end-to-end
- [ ] Metrics collection operational
- [ ] Admin panel displaying real-time data
- [ ] Read-only endpoints providing trace access
- [ ] Dashboard showing performance and cost metrics

### Milestone 6: Production Ready (E8-E9)
**Acceptance Criteria**:
- [ ] Comprehensive test suite passing
- [ ] Load testing meeting performance targets
- [ ] Canary deployment working
- [ ] Rollback procedures tested and documented
- [ ] Production monitoring and alerting operational

## 3. Risks & Mitigations

### Risk 1: Single Point of Failure (SPOF)
**Impact**: High - Gateway failure affects all AI functionality
**Mitigation**: 
- Implement circuit breaker to local fallbacks
- Deploy gateway in high availability configuration
- Maintain existing AI service as emergency fallback
- Health checks and automatic failover

### Risk 2: Cost Runaway
**Impact**: High - Uncontrolled AI API costs
**Mitigation**:
- Hard budget caps with automatic shutdown
- Real-time cost tracking and alerts
- Per-request cost limits
- Daily/monthly spending thresholds

### Risk 3: PII Leakage
**Impact**: Critical - Sensitive data exposure
**Mitigation**:
- Comprehensive PII detection and masking
- Audit logging for all data access
- Regular security reviews
- Compliance with data protection regulations

### Risk 4: Latency Inflation
**Impact**: Medium - Degraded user experience
**Mitigation**:
- Aggressive caching strategies
- Connection pooling and optimization
- Performance monitoring and alerting
- Target ≤50ms overhead

### Risk 5: Integration Complexity
**Impact**: Medium - Breaking existing functionality
**Mitigation**:
- Incremental rollout with feature flags
- Comprehensive integration testing
- Backward compatibility preservation
- Quick rollback procedures

## 4. Config & Feature Flags

### Environment Variables
```bash
# AI Gateway Control
AI_GATEWAY_ENABLED=false                    # Master toggle
AI_GATEWAY_EXPERIMENTAL=false               # Scaffolding mode

# Provider Configuration
AI_OPENAI_API_KEY=CHANGEME                  # OpenAI API key
AI_OPENAI_MODEL=gpt-3.5-turbo              # Default model
AI_OPENAI_TIMEOUT=5                         # Timeout in seconds
AI_OPENAI_MAX_RETRIES=3                     # Retry attempts

# Policy Configuration
AI_RATE_LIMIT_PER_USER=20                   # Requests per minute
AI_RATE_LIMIT_PER_IP=100                    # Requests per minute
AI_BUDGET_MONTHLY=500                       # Monthly budget in USD
AI_BUDGET_DAILY=20                          # Daily budget in USD

# Fallback Configuration
AI_FALLBACK_ENABLED=true                    # Enable fallbacks
AI_FALLBACK_ORDER=openai,local              # Fallback sequence
AI_CIRCUIT_BREAKER_ENABLED=true             # Circuit breaker

# Observability
AI_TRACING_ENABLED=true                     # Request tracing
AI_METRICS_ENABLED=true                     # Metrics collection
AI_LOG_LEVEL=INFO                           # Logging level
```

### Database Configuration
```sql
-- AI Configuration Table
CREATE TABLE ai_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER REFERENCES users(id)
);

-- Feature Flags Table
CREATE TABLE ai_feature_flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Hot-Reload Expectations
- **Policy Changes**: Immediate effect (< 5 seconds)
- **Provider Configuration**: 30-second grace period
- **Feature Flags**: Immediate effect
- **Budget Limits**: Real-time enforcement
- **Fallback Order**: 10-second propagation

## 5. Test Strategy

### Unit Testing
**Scope**: Individual components and interfaces
**Targets**:
- AIProvider implementations
- Policy engine logic
- Context builder and normalizer
- Circuit breaker functionality
- PII detection utilities

**Tools**: pytest, unittest.mock
**Coverage Target**: 90%+

### Integration Testing
**Scope**: Component interactions and workflows
**Targets**:
- Orchestrator → Provider → Normalizer flow
- Policy enforcement integration
- Fallback chain execution
- Configuration hot-reload
- End-to-end request processing

**Tools**: pytest, testcontainers
**Coverage Target**: 80%+

### End-to-End Testing
**Scope**: Complete user workflows
**Targets**:
- Bot search flow with AI
- API search endpoints
- Admin panel functionality
- Feature flag toggling
- Error handling and recovery

**Tools**: pytest, playwright
**Coverage Target**: 70%+

### Chaos Testing
**Scope**: Failure scenarios and recovery
**Targets**:
- Provider timeouts and failures
- Rate limiting and throttling
- Circuit breaker activation
- Budget limit enforcement
- Network partitions

**Tools**: pytest, chaos-engineering
**Coverage Target**: Critical paths only

### Load Testing
**Scope**: Performance and scalability
**Targets**:
- Concurrent request handling
- Memory usage under load
- Response time degradation
- Provider rate limit handling
- Database performance

**Tools**: locust, k6
**Targets**: 1000 RPS, <100ms p95 latency

## 6. Phase 0 (Optional Scaffolding Proposal)

### Scaffolding Approach
If approved, create empty files/classes behind `AI_GATEWAY_EXPERIMENTAL=false` to establish the structure without changing behavior.

### Files to Create
```
app/services/
├── ai_provider.py          # Base provider interface
├── ai_client.py           # Unified client skeleton
├── ai_orchestrator.py     # Orchestration logic
├── ai_context.py          # Context management
├── ai_normalizer.py       # Response normalization
├── ai_policy_engine.py    # Policy enforcement
├── ai_fallbacks.py        # Fallback orchestration
└── ai_logging.py          # Masked logging

app/providers/
├── __init__.py
├── openai_provider.py     # OpenAI implementation
└── stub_provider.py       # Mock provider for testing

app/models/
├── ai_config.py           # Configuration models
├── ai_trace.py           # Trace data models
└── ai_metrics.py         # Metrics models

app/api/routers/
└── ai_admin.py           # Admin API endpoints

tests/
├── unit/ai/              # Unit tests
├── integration/ai/       # Integration tests
└── chaos/ai/            # Chaos tests
```

### Implementation Notes
- All classes implement basic interfaces with no-op methods
- Configuration system ready but not active
- Database migrations prepared but not applied
- Tests written but not executed
- Documentation complete
- **STOP after scaffold creation - wait for explicit approval**

## 7. Open Questions

1. **High Availability Requirements**: What are the specific HA requirements for the AI Gateway? Should it be deployed as a separate service or integrated into the existing FastAPI application?

2. **Exact Performance Targets**: What are the precise latency and throughput targets for the gateway? The RFC mentions ≤50ms overhead, but what are the absolute response time requirements?

3. **Budget Cap Configuration**: Who can modify budget limits and under what conditions? Should there be different budget levels for different environments (dev/staging/production)?

4. **Data Retention Windows**: What are the specific retention requirements for traces, metrics, and audit logs? Are there compliance requirements that affect data storage duration?

5. **Policy Edit Permissions**: Who has the authority to modify AI policies in production? Should there be approval workflows for sensitive policy changes?

6. **Monitoring Integration**: Which existing monitoring tools should the AI Gateway integrate with? Are there specific metrics dashboards or alerting systems that need to be updated?

7. **Rollout Timeline**: What is the target timeline for the complete rollout? Are there specific business milestones or deadlines that affect the implementation schedule?
