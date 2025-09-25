# Authentication Vision and Policies

## 1. Executive Summary

This document establishes unified goals and guardrails for authentication across the Backend API, Web (customer-facing) SPA, and Admin Panel SPA. The intent is to eliminate current inconsistencies in token claims, TTL configurations, and JWT library usage while standardizing frontend handling patterns including storage keys, interceptors, and error management. The vision prioritizes strengthening the security posture through consistent storage mechanisms, clear logout semantics, and explicit policies for refresh tokens, while maintaining a clear delineation between public and protected endpoints across all components.

## 2. Goals (Verbatim + Clarified)

- **Unify token claims and decoding path across the API**: Establish a single, consistent JWT structure with standardized claim names and validation logic used by all backend services
- **Use a single JWT library (or a single abstraction) everywhere**: Eliminate the current dual python-jose/PyJWT imports and consolidate on one library with consistent error handling
- **Align token TTLs and how they are communicated to clients**: Resolve the 30-minute configuration vs 24-hour response discrepancy and ensure consistent TTL communication
- **Standardize frontend handling (storage key, interceptor, error/expiry handling)**: Unify the `auth_token` vs `access_token` storage key difference and implement consistent HTTP interceptor patterns across both SPAs
- **Define a clear policy for refresh tokens (or explicitly no-refresh)**: Establish whether refresh tokens will be implemented or explicitly document the no-refresh stateless approach
- **Strengthen security posture (storage choice, CSRF/XSS considerations, logout semantics)**: Address localStorage XSS vulnerabilities and define clear logout behavior including server-side token handling
- **Keep public endpoints policy explicit (which routes remain public, which guarded)**: Document and enforce consistent authentication requirements across all API endpoints

## 3. Policy Matrix (Task Type × Policy)

| Task Type | Token Type | TTL | Refresh Policy | Storage | Header Usage | Permission Check | Error Handling | Audit/Logging |
|-----------|------------|-----|----------------|---------|--------------|------------------|----------------|---------------|
| **login** | JWT | 30min | no-refresh | localStorage | N/A | user.is_active | standardized | success/failure |
| **protected_api_call** | JWT | validate | N/A | read from storage | Authorization: Bearer | role+permission | 401→clear+redirect | sensitive actions |
| **optional_auth_call** | JWT | validate | N/A | read from storage | Authorization: Bearer | context-aware | graceful degradation | optional tracking |
| **logout** | JWT | immediate | N/A | clear from storage | Authorization: Bearer | authenticated | clear local state | logout events |
| **token_refresh** | N/A | N/A | disabled | N/A | N/A | N/A | N/A | N/A |
| **admin_only_call** | JWT | validate | N/A | read from storage | Authorization: Bearer | admin roles | 403→permission denied | all admin actions |

## 4. Claims & Token Standards

### Canonical Claims Structure
```json
{
  "sub": "USER_ID",           // User ID as integer (not username)
  "role": "admin|manager|pro|user", 
  "exp": 1234567890,          // Unix timestamp
  "iat": 1234567890,          // Issued at timestamp
  "jti": "unique-token-id"    // Optional: for token revocation lists
}
```

### Legacy Claims Handling
- Current `sub=username` patterns should be migrated to `sub=user_id` during transition period
- Both validation paths may temporarily coexist with deprecation warnings
- `user_id` claim (when present) takes precedence over `sub=username` interpretations

### Technical Standards
- **Signing Algorithm**: HS256 (current standard maintained)
- **Key Management**: Configuration-driven secret key rotation capability
- **TTL Source**: Configuration value (jwt_access_token_expire_minutes) must match response field (expires_in)
- **Library Standard**: Single JWT library choice to be determined (python-jose vs PyJWT)

## 5. Frontend Handling (Web & Admin)

### Storage Standards
- **Default Method**: localStorage (current approach maintained)
- **Alternative Consideration**: HTTPOnly cookies for enhanced XSS protection (future evaluation)
- **Unified Storage Key**: `access_token` (Admin Panel key adopted as standard)
- **Cross-SPA Session**: Single token enables access to both Web and Admin interfaces (when user has appropriate permissions)

### HTTP Client Standards
- **Request Interceptor**: Automatic Authorization header injection for all authenticated requests
- **Response Interceptor**: Standardized 401/403 handling with automatic token cleanup
- **Error Handling Pattern**: 
  - 401 → Clear token + redirect to login
  - 403 → Display permission denied message
  - Network errors → Graceful degradation with retry capability

### UX Expectations
- **Token Expiry**: Redirect to login (no refresh tokens means no silent refresh)
- **Session Management**: Clear visual indicators for authentication state
- **Permission Gates**: Frontend UI hints based on user role (server remains source of truth)

## 6. Authorization & Roles

### Server-Side Authority
- **Source of Truth**: Backend permission validation through dependency injection
- **Role Hierarchy**: super_admin > admin > manager > operator > pro > fleet > user
- **Permission Mapping**: Server-side `has_permission()` method remains authoritative

### Client-Side Hints
```yaml
Frontend Permission Gates:
  - isAdmin: role in ['super_admin', 'admin']
  - isManager: role in ['super_admin', 'admin', 'manager']
  - isPro: role in ['pro', 'fleet']
  - Purpose: UI feature gating only (not security enforcement)
```

### Minimal Role→Permission Mapping
- **super_admin**: All permissions (*)
- **admin**: User, part, order, lead management
- **manager**: Read operations + limited write operations
- **operator**: Operational tasks only
- **pro/fleet**: Enhanced pricing visibility
- **user**: Basic customer operations

## 7. Security Considerations

### XSS/CSRF Protection
- **localStorage Risk**: Acknowledged XSS vulnerability with client-side token access
- **CSRF Mitigation**: CORS policy restricts origins; no additional CSRF tokens currently
- **Future Enhancement**: HTTPOnly cookie evaluation for sensitive operations

### Logout Semantics
- **Current Approach**: Stateless logout (client-side token removal only)
- **Rationale**: Simplicity and scalability with short-lived tokens
- **Alternative**: Server-side revocation list for high-security requirements (future consideration)

### Access Control
- **Rate Limiting**: Authentication endpoint protection against brute force
- **IP Allowlist**: Optional consideration for admin endpoints
- **Account Locking**: Existing failed attempt tracking maintained

### Audit/Logging Requirements
- **Login Events**: Success/failure with IP and user agent
- **Admin Actions**: All administrative operations logged
- **Permission Denials**: 403 responses tracked for security monitoring
- **Token Issues**: Invalid token attempts logged

## 8. Config Schema (Non-binding Sketch)

```yaml
auth:
  jwt:
    library: "python-jose"           # Single library choice
    algorithm: "HS256"
    access_ttl_minutes: 30
    refresh_enabled: false           # Explicit no-refresh policy
    claims:
      sub_format: "user_id"          # vs "username" (legacy)
      required: ["sub", "role", "exp", "iat"]
      optional: ["jti"]
  
  frontend:
    storage: "localStorage"          # vs "cookie_httponly" (future)
    token_key: "access_token"        # Unified key name
    interceptor: true                # Auto-inject headers
    on_401: "redirect_login"         # vs "silent_refresh" (disabled)
    on_403: "show_permission_error"
  
  security:
    cors_origins: ["http://localhost:5173", "http://localhost:5174"]
    rate_limit_login: "5_per_minute"
    logout_behavior: "stateless"    # vs "revocation_list"
  
  permissions:
    model: "role_based"              # Current simple RBAC
    ui_hints: true                   # Frontend permission gates
    server_authoritative: true      # Backend remains source of truth
  
  public_routes:
    # Endpoints accessible without authentication
    - "/api/v1/health"
    - "/api/v1/vehicles"
    - "/api/v1/categories"
    - "/api/v1/parts"               # Read-only parts listing
    - "/api/v1/search"              # Public search functionality
  
  optional_auth_routes:
    # Endpoints that work with or without authentication
    - "/api/v1/pdp/**"              # Product detail pages
    - "/api/v1/sms/send"            # SMS notifications
  
  protected_routes:
    # All other routes require authentication
    - "/api/v1/users/**"
    - "/api/v1/admin/**"
    - "/api/v1/orders/**"
    - "/api/v1/leads/**"
  
  logging:
    auth_events: true               # Login/logout tracking
    admin_actions: true             # Administrative operation audit
    permission_denied: true         # 403 response logging
    token_validation_errors: false  # Reduce noise unless debugging
```

## 9. Observability & Compliance

### What to Log (Without PII)
- **Login Attempts**: Success/failure events with timestamp, IP address (hashed), user agent fingerprint
- **Token Operations**: Token issuance events, token decode failure rates, token expiry events
- **Authorization Events**: 401/403 response counts per route, permission denial reasons (role/permission name only)
- **Session Management**: Logout events, session timeout occurrences, concurrent session detection

### Suggested KPIs
- **Authentication Success Rate**: Successful logins / total login attempts
- **Authorization Error Rate**: 401/403 responses / total authenticated requests  
- **Average Login Latency**: Time from credential submission to token response
- **Token Validity Rate**: Valid token usage / total token validation attempts
- **Permission Utilization**: Most frequently accessed protected endpoints

### Retention Guidance
- **Authentication Logs**: 90 days for security analysis and compliance
- **Authorization Events**: 30 days for operational monitoring
- **Admin Action Audit**: 1 year for regulatory compliance
- **Error Rate Metrics**: 7 days for operational dashboards

## 10. Migration & Backward Compatibility (High-level)

The transition from current-state to unified policies should maintain zero-downtime compatibility through a phased approach. Backend services can temporarily support both JWT libraries during migration, with the primary library handling new token creation while the secondary validates existing tokens until their natural expiry. Frontend applications can implement feature flags to gradually adopt the unified storage key (`access_token`) and interceptor patterns, allowing for A/B testing and rollback capabilities. The token claim structure migration (sub=username to sub=user_id) requires a transition period where validation logic accepts both formats, with new tokens using the canonical structure while legacy tokens remain valid until expiration, ensuring no user sessions are disrupted during the policy implementation.

## 11. Open Questions (for Stakeholders)

1. **Storage Security Strategy**: Should we continue with localStorage for development simplicity, or migrate to HttpOnly cookies for enhanced XSS protection? What are the operational trade-offs you're willing to accept?

2. **Refresh Token Policy**: Do you want to enable refresh tokens for longer user sessions (y/n)? If yes, what TTLs (access: 30min, refresh: 7 days) and rotation policy (refresh-on-use vs fixed expiry)?

3. **Canonical Token Claims**: Should the final `sub` claim contain user_id (recommended) or username? This affects token portability and user lookup performance.

4. **Token Lifespan Strategy**: What's the target TTL for access tokens - 30 minutes (current config) or 24 hours (current response)? How should users experience token expiry (immediate redirect vs graceful notification)?

5. **JWT Library Consolidation**: Should we standardize on python-jose (current creation) or PyJWT (current validation), and what's the acceptable timeline for migration?

6. **Public Endpoint Policy**: Which endpoints must remain publicly accessible (vehicles, categories, search)? Are there currently unguarded endpoints that should now require authentication?

7. **Cross-Domain Session Strategy**: Are there plans for SSO across multiple subdomains or third-party integrations that would affect cookie vs localStorage strategy?

8. **Compliance and Audit Requirements**: What are the required retention windows for authentication logs (30 days, 90 days, 1 year)? Do you need real-time alerting for suspicious authentication patterns?

This configuration schema provides a declarative approach to authentication policies, enabling runtime adjustments without code deployment while maintaining clear boundaries between public, optional-auth, and protected functionality across the entire system.
