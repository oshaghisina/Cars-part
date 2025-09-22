# AI Admin Panel Specification

## 1. Objectives & Non-Goals

### Objectives
- **Control**: Complete oversight of AI traffic, policies, and provider management
- **Monitoring**: Real-time visibility into performance, costs, and system health
- **Configuration**: Dynamic policy adjustment without service restarts
- **Compliance**: PII protection, audit trails, and data governance
- **Troubleshooting**: Deep trace analysis and replay capabilities for debugging

### Non-Goals (MVP)
- **User Management**: No user creation/editing (handled by main admin panel)
- **Model Training**: No custom model fine-tuning or training interfaces
- **Advanced Analytics**: No ML-based insights or predictive analytics
- **Multi-Tenant**: Single-tenant system (no tenant isolation)
- **Real-time Chat**: No live chat support or help desk integration

## 2. Information Architecture

### 2.1 Overview Dashboard
**Purpose**: Real-time system health and key metrics at a glance
- Live traffic counters (requests/min, active users)
- Error rate trends and alerts
- Token usage and cost tracking (today vs yesterday)
- Provider health status and response times
- Circuit breaker status and fallback rates

### 2.2 Providers Management
**Purpose**: AI provider registry and configuration
- Provider list with health status, capabilities, and costs
- Add/remove provider configurations
- Suspend/resume individual providers
- Load balancing weights and routing rules
- API key management (masked display, test connectivity)
- Health check configuration and monitoring

### 2.3 Policies Configuration
**Purpose**: Centralized policy management and enforcement
- Rate limiting rules (per-user, per-IP, per-task-type)
- Timeout and retry configurations
- Budget limits and cost controls
- Model allowlist and restrictions
- Fallback order and circuit breaker settings
- Hot-reload status and change history

### 2.4 Prompts Management
**Purpose**: Prompt template versioning and testing
- Template library with version control
- Variable substitution and context injection
- Masked preview with PII detection
- A/B testing framework for prompt variations
- Test execution with sample data
- Performance metrics per template

### 2.5 Traces & Debugging
**Purpose**: Request tracing and debugging capabilities
- Search by request ID, user ID, time range, or task type
- Masked prompt/response viewing with reveal controls
- Request replay with safety guardrails
- Error analysis and root cause investigation
- Performance bottleneck identification
- Provider comparison and routing decisions

### 2.6 Feature Flags
**Purpose**: Runtime feature control and experimentation
- Master AI toggle (`ai_enabled`)
- Task-specific toggles (embeddings, chat, analysis)
- Bulk operation limits and controls
- Experimental features and beta flags
- Gradual rollout controls
- Impact monitoring and rollback capabilities

### 2.7 Alerts & Notifications
**Purpose**: Proactive monitoring and incident response
- Threshold configuration (error rates, latency, costs)
- Notification channel management (email, webhook, Slack)
- Alert history and acknowledgment
- Escalation policies and on-call rotation
- Custom alert rules and conditions
- Alert testing and validation

### 2.8 Audit Log
**Purpose**: Compliance and security audit trail
- Policy change history with user attribution
- Provider configuration modifications
- Replay actions and data access logs
- Security events and access attempts
- Data export and retention compliance
- Search and filtering capabilities

## 3. Data Contracts

### 3.1 Overview Dashboard
**Read Endpoints**:
- `GET /api/v1/ai/overview/metrics` - Real-time metrics
- `GET /api/v1/ai/overview/health` - System health status
- `GET /api/v1/ai/overview/costs` - Cost tracking data

**Payloads**:
```json
{
  "metrics": {
    "requests_per_minute": 45,
    "active_users": 12,
    "error_rate": 0.02,
    "p95_latency_ms": 850,
    "tokens_used_today": 125000,
    "cost_today": 12.50
  },
  "health": {
    "openai": "healthy",
    "anthropic": "degraded", 
    "local": "healthy"
  }
}
```

### 3.2 Providers Management
**Read Endpoints**:
- `GET /api/v1/ai/providers` - Provider list with status
- `GET /api/v1/ai/providers/{id}/health` - Provider health check

**Write Endpoints**:
- `POST /api/v1/ai/providers` - Add new provider
- `PUT /api/v1/ai/providers/{id}` - Update provider config
- `POST /api/v1/ai/providers/{id}/suspend` - Suspend provider
- `POST /api/v1/ai/providers/{id}/resume` - Resume provider
- `POST /api/v1/ai/providers/{id}/test` - Test connectivity

### 3.3 Policies Configuration
**Read Endpoints**:
- `GET /api/v1/ai/policies` - Current policy configuration
- `GET /api/v1/ai/policies/history` - Policy change history

**Write Endpoints**:
- `PUT /api/v1/ai/policies` - Update policies (with validation)
- `POST /api/v1/ai/policies/validate` - Validate policy changes
- `POST /api/v1/ai/policies/rollback/{version}` - Rollback to version

### 3.4 Prompts Management
**Read Endpoints**:
- `GET /api/v1/ai/prompts` - Template list with versions
- `GET /api/v1/ai/prompts/{id}/preview` - Masked preview
- `GET /api/v1/ai/prompts/{id}/metrics` - Performance metrics

**Write Endpoints**:
- `POST /api/v1/ai/prompts` - Create new template
- `PUT /api/v1/ai/prompts/{id}` - Update template
- `POST /api/v1/ai/prompts/{id}/test` - Test template execution

### 3.5 Traces & Debugging
**Read Endpoints**:
- `GET /api/v1/ai/traces` - Search traces (with pagination)
- `GET /api/v1/ai/traces/{id}` - Get specific trace
- `GET /api/v1/ai/traces/{id}/replay` - Get replay data

**Query Parameters**:
- `request_id`, `user_id`, `task_type`, `provider`
- `start_time`, `end_time`, `status`, `error_type`
- `page`, `limit`, `sort_by`, `sort_order`

**Write Endpoints**:
- `POST /api/v1/ai/traces/{id}/reveal` - Reveal masked data (audit required)
- `POST /api/v1/ai/traces/{id}/replay` - Replay request (with safeguards)

### 3.6 Feature Flags
**Read Endpoints**:
- `GET /api/v1/ai/flags` - Current flag states
- `GET /api/v1/ai/flags/history` - Flag change history

**Write Endpoints**:
- `PUT /api/v1/ai/flags` - Update flag states
- `POST /api/v1/ai/flags/{name}/toggle` - Toggle specific flag

### 3.7 Alerts & Notifications
**Read Endpoints**:
- `GET /api/v1/ai/alerts` - Alert configuration
- `GET /api/v1/ai/alerts/history` - Alert history
- `GET /api/v1/ai/alerts/channels` - Notification channels

**Write Endpoints**:
- `PUT /api/v1/ai/alerts` - Update alert configuration
- `POST /api/v1/ai/alerts/test` - Test alert delivery

### 3.8 Audit Log
**Read Endpoints**:
- `GET /api/v1/ai/audit` - Audit log entries (with pagination)
- `GET /api/v1/ai/audit/export` - Export audit data

**Query Parameters**:
- `user_id`, `action_type`, `resource_type`
- `start_time`, `end_time`, `severity`
- `page`, `limit`

## 4. Roles & Permissions (RBAC)

### 4.1 Admin Role
**Full Access**:
- All read operations across all pages
- Policy configuration and provider management
- Prompt template creation and modification
- Trace data revelation and replay operations
- Feature flag management
- Alert configuration and audit log access
- System configuration and maintenance

**Sensitive Actions** (require additional confirmation):
- Provider API key management
- Policy rollback operations
- Trace data revelation
- Request replay execution
- Budget limit modifications

### 4.2 Operator Role
**Limited Access**:
- Read-only access to Overview, Providers, Traces
- View-only access to Policies and Prompts
- Basic alert acknowledgment
- Limited audit log viewing (own actions only)

**Restricted Actions**:
- No policy modifications
- No provider configuration changes
- No trace data revelation
- No feature flag changes

### 4.3 Manager Role
**Moderate Access**:
- Full read access to all pages
- Policy viewing and basic modifications
- Provider status monitoring
- Alert configuration (non-critical)
- Limited trace analysis (masked data only)

**Restricted Actions**:
- No provider API key access
- No trace data revelation
- No request replay
- No budget limit changes

## 5. UX Notes

### 5.1 Data Masking
- **Default State**: All PII masked with `[REDACTED]` placeholders
- **Reveal Process**: Click "Reveal" → Enter reason → Admin approval → Time-limited access
- **Audit Trail**: All reveal actions logged with user, reason, and timestamp
- **Auto-Masking**: Sensitive data automatically detected and masked

### 5.2 Time Windows
- **Quick Selectors**: Last 15m, 1h, 24h, 7d, 30d
- **Custom Range**: Date/time picker with validation
- **Compare Mode**: Side-by-side comparison (today vs yesterday, this week vs last week)
- **Real-time Updates**: Live data refresh with configurable intervals

### 5.3 Safe Edit Patterns
- **Draft Mode**: Changes saved as drafts before application
- **Validation**: Real-time validation with error highlighting
- **Preview**: Impact preview before applying changes
- **Rollback**: Version history with one-click rollback
- **Approval**: Sensitive changes require admin approval

## 6. Metrics & Widgets (MVP)

### 6.1 Overview Cards
- **Requests/Min**: Live counter with trend indicator
- **P95 Latency**: Current and 24h average
- **Error Rate**: Percentage with trend chart
- **Token Usage**: Today's consumption with daily limit
- **Cost Tracking**: Today's spend with monthly budget
- **Active Users**: Current concurrent users

### 6.2 Provider Charts
- **Stacked Bar**: Requests by provider over time
- **Pie Chart**: Token usage distribution by provider
- **Line Chart**: Response time trends by provider
- **Heatmap**: Error rates by provider and task type

### 6.3 Data Tables
- **Top Errors**: Most frequent error types with counts
- **Top Routes**: Most used API endpoints with metrics
- **Fallback Rates**: Provider failure and fallback statistics
- **Cost Breakdown**: Spending by provider, task type, and user

## 7. Security, Privacy, Compliance

### 7.1 PII Redaction Standards
- **Send Data**: Names, emails, phone numbers, addresses masked
- **Receive Data**: AI responses scanned and redacted
- **Detection**: Regex patterns + ML-based detection
- **Retention**: PII data purged after 30 days

### 7.2 Access Controls
- **Authentication**: JWT tokens with role-based claims
- **Session Management**: 8-hour timeout with refresh
- **IP Allowlists**: Optional IP-based access restrictions
- **Audit Logging**: All actions logged with user attribution

### 7.3 Data Retention
- **Traces**: 90 days for debugging, 1 year for compliance
- **Audit Logs**: 2 years minimum retention
- **Metrics**: 1 year for historical analysis
- **PII Data**: 30 days maximum retention

## 8. Non-Functional Requirements

### 8.1 Performance Targets
- **API Response Time**: < 200ms for 95% of requests
- **Dashboard Load Time**: < 2 seconds initial load
- **Real-time Updates**: < 5 seconds data refresh
- **Search Performance**: < 500ms for trace searches

### 8.2 Availability
- **Uptime Target**: 99.9% availability
- **Degraded Mode**: Read-only mode during maintenance
- **Failover**: Automatic failover to backup systems
- **Recovery Time**: < 5 minutes for service restoration

### 8.3 Caching Strategy
- **Metrics Data**: 30-second cache for real-time metrics
- **Configuration**: 5-minute cache for policy data
- **Traces**: No caching for security reasons
- **Provider Status**: 1-minute cache with health checks

## 9. Open Questions

1. **Dashboard Technology**: Should we use a specific dashboard framework (Grafana, custom React components) or build native admin panel integration?

2. **Retention Limits**: What are the specific data retention requirements for different data types, and are there any regulatory compliance requirements (GDPR, CCPA)?

3. **Export Capabilities**: What export formats are needed for audit logs and trace data (CSV, JSON, PDF reports), and what are the volume limits?

4. **SSO Integration**: Should the AI admin panel integrate with existing SSO systems, or maintain separate authentication with the main admin panel?

5. **Audit Retention**: How long should audit logs be retained, and what are the requirements for secure deletion and compliance reporting?

6. **Replay Safeguards**: What specific safeguards are needed for request replay (rate limiting, data sanitization, approval workflows) to prevent abuse?

7. **Real-time Scaling**: What are the expected concurrent admin users and real-time data volume, and how should we scale the WebSocket connections for live updates?
