# Authentication Implementation Plan

## 1. Milestones & Timeline

### M1: Backend Consolidation (Weeks 1-2)
- **Objective**: Unify JWT library, standardize token claims, align TTL configuration
- **Deliverables**: Single JWT library in use, `sub=user_id` canonical format, config/response TTL match
- **Duration**: 2 weeks

### M2: Frontend Unification (Weeks 3-4)
- **Objective**: Standardize storage keys and HTTP interceptor patterns across both SPAs
- **Deliverables**: Unified `access_token` storage, centralized Admin Panel API client, consistent error handling
- **Duration**: 2 weeks

### M3: Policy Exposure (Week 5)
- **Objective**: Create configuration endpoints and basic admin panel policy viewer
- **Deliverables**: `/api/v1/auth/config` endpoint, read-only policy display in admin interface
- **Duration**: 1 week

### M4: Admin Panel Integration (Weeks 6-7)
- **Objective**: Implement authentication monitoring dashboard
- **Deliverables**: Overview metrics, audit log viewer, token analytics basic functionality
- **Duration**: 2 weeks

### M5: Migration Cutover (Week 8)
- **Objective**: Remove legacy support and finalize unified authentication
- **Deliverables**: Single JWT library only, canonical claims enforced, unified storage key mandatory
- **Duration**: 1 week

### M6: Validation & Rollout (Week 9)
- **Objective**: Staging validation and production deployment
- **Deliverables**: Smoke tests passing, blue/green deployment completed, monitoring operational
- **Duration**: 1 week

### M7: Optional Hardening (Week 10)
- **Objective**: Enhanced security features and operational monitoring
- **Deliverables**: Alert thresholds configured, brute-force detection active, audit retention policy enforced
- **Duration**: 1 week

## 2. Work Breakdown

### Backend Changes
- **app/core/auth.py**: Update `create_access_token()` to use canonical claims (`sub=user_id`)
- **app/api/dependencies.py**: Consolidate to single JWT library, remove dual validation paths
- **app/api/routers/users.py**: Align `expires_in` response with configuration TTL value
- **app/services/user_service.py**: Update authentication logic for unified claim format
- **app/api/routers/auth.py**: New endpoints for configuration exposure and metrics

### Frontend Web Changes
- **app/frontend/web/src/stores/auth.js**: Migrate storage key from `auth_token` to `access_token`
- **app/frontend/web/src/api/pdp.js**: Verify interceptor compatibility with unified storage key
- **app/frontend/web/src/components/auth/LoginModal.vue**: Update error handling for standardized responses

### Frontend Panel Changes
- **app/frontend/panel/src/api/client.js**: Create centralized API client with interceptors (new file)
- **app/frontend/panel/src/stores/auth.js**: Update to use centralized client and unified error handling
- **app/frontend/panel/src/stores/*.js**: Migrate all stores to use centralized client with auto-auth headers
- **app/frontend/panel/src/views/AuthDashboard.vue**: New authentication monitoring interface

### Admin Panel Integration
- **app/frontend/panel/src/components/auth/**: Metrics widgets, audit log table, policy viewer components
- **app/frontend/panel/src/router/index.js**: Add authentication monitoring routes
- **app/api/routers/auth_admin.py**: New endpoints for authentication metrics and audit data

### CI/CD Integration
- **tests/integration/test_auth_flow.py**: Login/logout/protected route smoke tests
- **tests/unit/test_jwt_validation.py**: Unified JWT library validation tests
- **.github/workflows/**: Add authentication flow validation to deployment pipeline

## 3. Acceptance Criteria per Milestone

### M1: Backend Consolidation
- ✅ Only one JWT library imported across entire backend codebase
- ✅ All new tokens contain `sub=user_id` (integer) instead of username
- ✅ `jwt_access_token_expire_minutes` configuration matches `expires_in` response field
- ✅ Legacy `sub=username` validation maintained for transition period

### M2: Frontend Unification
- ✅ Both Web and Admin SPAs use `access_token` localStorage key
- ✅ Admin Panel has centralized API client with automatic Authorization header injection
- ✅ Consistent 401→clear token+redirect and 403→permission error handling across SPAs
- ✅ Cross-SPA session compatibility (login in one SPA enables access to other)

### M3: Policy Exposure
- ✅ `GET /api/v1/auth/config` returns current JWT library, TTL, claims format, public routes
- ✅ Admin Panel displays authentication configuration in read-only policy viewer
- ✅ Configuration endpoint restricted to admin-only access

### M4: Admin Panel Integration
- ✅ Overview dashboard shows auth success rate, error rate, login latency (p50/p95)
- ✅ Token analytics display recent issuance events and decode failure patterns
- ✅ Audit log viewer shows login events with PII masking (hashed IP, user role only)

### M5: Migration Cutover
- ✅ Zero JWT decode mismatches in application logs after legacy support removal
- ✅ PyJWT imports removed from codebase (if python-jose chosen as standard)
- ✅ `auth_token` storage key support removed from Web SPA
- ✅ All authentication flows use canonical token format

### M6: Validation & Rollout
- ✅ Staging environment smoke tests pass for login, protected routes, cross-SPA compatibility
- ✅ Production deployment completed via blue/green strategy with zero downtime
- ✅ Authentication monitoring dashboard operational for admin users

## 4. Risks & Mitigations

### Dual Library Confusion Risk
- **Risk**: Inconsistent token validation during transition period
- **Mitigation**: Phased removal with comprehensive logging; maintain python-jose as primary throughout migration

### Legacy Token Claim Rejection Risk
- **Risk**: Existing user sessions invalidated during `sub=username` to `sub=user_id` migration
- **Mitigation**: 8-week transitional period supporting both claim formats; gradual enforcement with monitoring

### Storage Key Migration Risk
- **Risk**: Users lose sessions during `auth_token` to `access_token` migration
- **Mitigation**: Temporary dual key support in Web SPA; migration notification in UI; gradual cutover

### Admin Panel Interceptor Risk
- **Risk**: API calls fail if centralized client interceptor implementation has issues
- **Mitigation**: Feature flag for interceptor usage; fallback to manual Authorization header attachment; comprehensive testing

### TTL Configuration Mismatch Risk
- **Risk**: Config/response value misalignment causes client-side token handling issues
- **Mitigation**: Automated tests validating TTL parity; monitoring for decode timing discrepancies

## 5. Observability & Monitoring

### Synthetic Testing
- **Login Flow Test**: Automated credential validation every 5 minutes
- **Protected Route Test**: Token-required endpoint accessibility validation
- **Cross-SPA Test**: Login in Web SPA, verify Admin Panel access with same token
- **TTL Validation Test**: Verify token expiry timing matches configuration

### Key Metrics
- **Authentication Success Rate**: Target ≥99% for valid credentials
- **Authorization Error Rate**: Target ≤1% for authenticated requests (401/403 combined)
- **Login Latency**: Target p95 ≤500ms, p50 ≤200ms
- **Decode Error Count**: Track JWT validation failures by error type (expired/invalid/malformed)

### Admin Dashboard
- **Real-time Metrics**: Authentication health indicators updated every 30 seconds
- **Historical Trends**: 24-hour authentication pattern visualization
- **Error Pattern Analysis**: Route-specific failure rate breakdown
- **Performance Monitoring**: Login latency distribution and outlier detection

### Alerting Framework
- **Error Rate Threshold**: >5% authentication failures over 15-minute window
- **Latency Threshold**: p95 login latency >1000ms sustained for 5 minutes
- **Decode Failure Spike**: >10 JWT validation errors per minute
- **Brute Force Detection**: >20 failed attempts from single IP in 10 minutes

## 6. Rollout & Backout Plan

### Rollout Strategy
1. **Backend Deploy**: Blue/green deployment with unified JWT library and canonical claims
2. **Frontend Staging**: Deploy storage key migration to staging environment first
3. **Admin Panel Update**: Deploy centralized client and authentication dashboard
4. **Production Cutover**: Coordinate release of backend + both frontend SPAs
5. **Legacy Cleanup**: Remove transitional support after 8-week validation period

### Backout Strategy
- **Immediate Rollback**: Revert to previous deployment image via blue/green switch
- **Library Restoration**: Re-enable PyJWT validation path in app/api/dependencies.py
- **Claims Fallback**: Restore `sub=username` token creation and dual validation support
- **Storage Key Revert**: Re-enable `auth_token` support in Web SPA with configuration flag
- **Monitoring Reset**: Disable new authentication admin panel features if causing issues

### Validation Checkpoints
- **Pre-deploy**: All synthetic tests passing in staging environment
- **Post-deploy**: Authentication success rate >95% within first hour
- **24-hour Mark**: No increase in support tickets related to login issues
- **Week 1**: Admin panel authentication monitoring fully operational

## 7. Timeline Sketch

```
Week 1-2: Backend Consolidation (M1)
├── Week 1: JWT library selection, TTL alignment, claim format update
└── Week 2: Legacy compatibility layer, validation testing

Week 3-4: Frontend Unification (M2) 
├── Week 3: Web SPA storage migration, Admin Panel client creation
└── Week 4: Error handling standardization, cross-SPA testing

Week 5: Policy Exposure (M3)
└── Configuration endpoints, admin panel policy viewer

Week 6-7: Admin Panel Integration (M4)
├── Week 6: Metrics dashboard, audit log viewer
└── Week 7: Token analytics, error pattern visualization

Week 8: Migration Cutover (M5)
└── Legacy support removal, validation cleanup

Week 9: Validation & Rollout (M6)
└── Staging validation, production deployment

Week 10: Optional Hardening (M7)
└── Alert configuration, brute-force detection
```

### Parallelizable Tasks
- Backend JWT library consolidation can proceed while frontend storage key migration develops
- Admin Panel authentication dashboard can be built against mock data before backend metrics endpoints
- Policy viewer implementation can proceed using current configuration reading patterns

### Sequential Dependencies
- Frontend unification requires backend claim standardization completion
- Admin panel integration requires backend metrics endpoints availability
- Migration cutover requires all frontend changes deployed and validated

## 8. Open Questions

1. **JWT Library Selection**: Should we standardize on python-jose (current token creation) or PyJWT (current validation), and what's the final decision deadline for development planning?

2. **TTL Final Configuration**: Confirm 30-minute access token lifespan versus 24-hour alternative, considering user workflow requirements and security posture?

3. **Admin Panel Metrics Scope**: Should authentication monitoring be a standalone section or integrated into existing system monitoring dashboard in the admin panel?

4. **Alert Threshold Tuning**: What authentication error rates warrant immediate notification (1%, 5%, 10%) and who should receive these alerts in the operational team?

5. **Audit Log Retention Policy**: Confirm 90-day retention for authentication events meets compliance requirements, or adjust based on regulatory needs?

6. **Brute Force Detection**: What failed login attempt thresholds (per IP, per user) should trigger account lockout or IP blocking, and what unlock procedures are required?

7. **Operational Team Ownership**: Who will be responsible for monitoring authentication health post-deployment, and what escalation procedures are needed for authentication system incidents?
