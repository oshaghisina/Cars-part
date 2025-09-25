# Authentication Admin Panel Specification

## 1. Objectives & Non-Goals

### Objectives
- **Observe**: Monitor authentication success/failure rates, login latency, and token validation performance across Web and Admin SPAs
- **Troubleshoot**: Identify failing routes, decode error patterns, and user authentication issues through aggregated metrics
- **Configure**: View current authentication policies and configuration (library, TTL, storage, public routes) with read-only access in MVP
- **Alert**: Basic threshold monitoring for auth error rates and failed login attempts with configurable notification channels

### Non-Goals (MVP)
- User self-service password reset or profile management
- Real-time session termination or token revocation capabilities
- Granular permission editing or role assignment interfaces
- Advanced analytics beyond authentication flow monitoring
- Configuration editing (read-only policy display only)

## 2. Information Architecture

### Overview Dashboard
**Purpose**: High-level authentication health monitoring
- Current system status (library version, TTL configuration, active user count)
- Real-time authentication metrics (success rate, error rate, average latency)
- Visual trend indicators for last 24 hours

### Sessions/Tokens Monitor (Read-only)
**Purpose**: Token lifecycle and validation monitoring
- Recent token issuance events (count by SPA, no token strings exposed)
- Decode failure patterns (JWT expiry vs invalid signature vs malformed)
- Top routes generating 401/403 responses with request volume

### Policies Viewer
**Purpose**: Current configuration display
- Active JWT library and algorithm
- Token TTL configuration and actual response values
- Public vs protected route classification
- Storage mechanism and security policies

### Alerts Configuration
**Purpose**: Basic threshold monitoring setup
- Error rate thresholds (401/403 percentage triggers)
- Failed login attempt limits (per IP, per user)
- Notification channels (email, Telegram) - placeholder configuration

### Audit Log
**Purpose**: Authentication event tracking
- Login success/failure events (timestamp, user role, hashed IP)
- Admin panel access events (page views, configuration views)
- Future: policy change events when editing becomes available

## 3. Data Contracts (Lightweight)

### Overview Metrics
```
GET /api/v1/admin/auth/metrics
Query params: time_window=1h|24h|7d (default: 24h)
Response: {
  success_rate: 99.2,
  error_rate: 0.8,
  login_latency_p50: 180,
  login_latency_p95: 450,
  active_sessions: 45,
  library_version: "python-jose-3.3.0"
}
```

### Token Analytics
```
GET /api/v1/admin/auth/tokens
Query params: time_window, spa_filter=web|admin, limit=100
Response: {
  recent_issues: [{timestamp, spa_type, user_role, success}],
  decode_failures: [{timestamp, error_type, route, count}],
  top_401_routes: [{route, count, percentage}]
}
```

### Audit Events
```
GET /api/v1/admin/auth/audit
Query params: time_window, event_type, skip, limit
Response: {
  events: [{timestamp, event_type, user_role, ip_hash, details}],
  total: 1250,
  filtered: 45
}
```

### Configuration View
```
GET /api/v1/admin/auth/config
Response: {
  jwt_library: "python-jose",
  ttl_minutes: 30,
  storage_type: "localStorage",
  public_routes: ["/health", "/vehicles"],
  protected_routes_count: 25
}
```

## 4. RBAC

### Access Levels
- **Admin Role**: Full read access to all authentication data and audit logs
- **Operator Role**: Read-only access to metrics and current session monitoring (no audit log access)
- **Manager Role**: Dashboard view only (aggregated metrics without detailed failure data)

### Data Masking
- **IP Addresses**: Always hashed (SHA-256) in UI display
- **User Identifiers**: Show user role and ID, mask username/email
- **Token Strings**: Never exposed in any UI context
- **Sensitive Routes**: Mask parameter values in failed request logs

### Future Sensitive Operations
- **Configuration Changes**: Admin-only when editing becomes available
- **Session Termination**: Admin-only for emergency account lockout
- **Audit Data Export**: Admin-only with approval workflow

## 5. UX Notes

### Default Time Windows
- **Dashboard Metrics**: Last 24 hours (with 15min/1h/7d quick filters)
- **Token Analytics**: Last 1 hour (with 15min/4h/24h options)
- **Audit Logs**: Last 7 days (with 1d/30d options)

### Empty States
- **No Recent Activity**: "No authentication events in selected time window"
- **No Failed Logins**: "All login attempts successful in selected period"
- **No Configuration**: "Authentication policies loading..." with refresh option

### Error States
- **Metrics Unavailable**: "Authentication metrics temporarily unavailable" with retry
- **Data Loading Failed**: "Unable to load authentication data" with manual refresh
- **Permission Denied**: "Insufficient permissions to view authentication details"

### Terminology Consistency
- **Claims**: JWT token data fields (sub, role, exp, iat)
- **TTL**: Token Time-To-Live in minutes
- **Decode Errors**: JWT validation failures (expiry, signature, format)
- **Auth Events**: Login, logout, token validation activities

## 6. Metrics & Widgets (MVP)

### Dashboard Cards
- **Auth Success Rate**: 99.2% (last 24h) with trend indicator ↑↓
- **401/403 Error Rate**: 0.8% (last 24h) with threshold alert indicator
- **Average Login Latency**: 180ms (p50) / 450ms (p95) with performance trend
- **Decode Error Count**: 12 errors (last 1h) with error type breakdown

### Charts
- **Stacked Area Chart**: Authentication events by SPA (Web vs Admin Panel) over time
- **Line Chart**: Login latency trend (p50/p95) with 15-minute granularity
- **Bar Chart**: Top failing routes with 401/403 breakdown
- **Pie Chart**: Error distribution (expired vs invalid vs malformed tokens)

### Tables
- **Recent Failed Logins**: Timestamp, IP hash, user role, failure reason (limit 20)
- **Top Error Routes**: Route path, method, error count, percentage of total requests
- **Token Issue Summary**: SPA type, successful issues, decode failures, time window

## 7. Security & Privacy

### PII Redaction Policies
- **IP Address Hashing**: SHA-256 with application salt, display last 8 characters
- **User Identification**: Show user ID and role, redact username/email/phone
- **Request Parameters**: Mask sensitive data in failed request logs
- **Timestamp Precision**: Round to nearest minute for privacy in long-term storage

### Retention Windows
- **Authentication Metrics**: 30 days rolling window for dashboard display
- **Audit Events**: 90 days retention for compliance and security analysis
- **Error Logs**: 7 days for operational troubleshooting
- **Performance Metrics**: 24 hours high-resolution, 30 days daily aggregates

### Access Logging
- **Admin Panel Views**: Log authentication admin page access with user ID and timestamp
- **Configuration Access**: Track policy viewer usage for audit purposes
- **Data Export**: Log any future audit data export with approval workflow
- **Search/Filter Usage**: Track admin investigation patterns for security monitoring

### Token Security
- **No Token Exposure**: JWT strings never displayed in UI under any circumstances
- **Decode Information Only**: Show claims data (user_id, role) without token reconstruction capability
- **Validation Context**: Display decode success/failure without token content access

## 8. Open Questions

1. **Alert Thresholds**: What authentication error rate (401/403) percentage should trigger alerts - 1%, 5%, or 10% over what time window?

2. **Retention Policy Confirmation**: Are the proposed retention windows (30d metrics, 90d audit, 7d errors) sufficient for operational and compliance needs?

3. **Data Masking Granularity**: Should IP address hashing be configurable per deployment environment, or maintain consistent SHA-256 across all environments?

4. **Export Capabilities**: Do you need CSV/JSON export functionality for audit logs and metrics data, and if so, what approval workflow is required?

5. **Session Revocation Priority**: When should we implement emergency session termination capabilities, and what role restrictions apply?

6. **Real-time Monitoring**: Do you need real-time dashboard updates (WebSocket) or is periodic refresh (30-60 seconds) sufficient for authentication monitoring?

7. **Integration Requirements**: Should authentication alerts integrate with existing monitoring systems (Slack, PagerDuty) or remain email/Telegram only for the MVP phase?
