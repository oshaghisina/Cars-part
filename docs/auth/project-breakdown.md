# Authentication System Project Breakdown & Planning

## 📋 Project Overview

**Objective**: Implement unified authentication system with dual login (Email/Password + Phone/OTP) and Telegram SSO integration.

**Timeline**: 16 weeks (4 months)  
**Team**: Backend, Frontend, DevOps, QA  
**Status**: Ready for Development

## 🎯 Success Criteria

- ✅ Unified JWT authentication across Web and Admin SPAs
- ✅ Phone + OTP authentication using existing SMS service
- ✅ Telegram account linking (Web ↔ Bot)
- ✅ Comprehensive admin monitoring dashboard
- ✅ Security hardening with rate limiting and audit logging

## 📅 Phase 1: Core Authentication Unification (Weeks 1-8)

### Week 1-2: Backend Foundation
**Owner**: Backend Team  
**Deliverables**: JWT library consolidation, TTL alignment, canonical claims

#### Tasks:
- [ ] **M1.1**: Choose single JWT library (python-jose recommended)
- [ ] **M1.2**: Update `app/api/dependencies.py` to use unified library
- [ ] **M1.3**: Fix TTL mismatch (config: 30min, response: 24h)
- [ ] **M1.4**: Implement canonical claims (`sub=user_id` instead of username)
- [ ] **M1.5**: Add transitional support for legacy `sub=username`
- [ ] **M1.6**: Create comprehensive JWT validation tests

#### Acceptance Criteria:
- Only one JWT library imported across backend
- All new tokens use `sub=user_id` format
- TTL configuration matches API response
- Legacy token validation maintained

#### Files to Modify:
```
app/core/auth.py
app/api/dependencies.py
app/api/routers/users.py
app/core/config.py
tests/unit/test_jwt_validation.py
```

### Week 3-4: Frontend Unification
**Owner**: Frontend Team  
**Deliverables**: Unified storage keys, HTTP interceptors, error handling

#### Tasks:
- [ ] **M2.1**: Migrate Web SPA storage key from `auth_token` to `access_token`
- [ ] **M2.2**: Create centralized API client for Admin Panel
- [ ] **M2.3**: Implement automatic Authorization header injection
- [ ] **M2.4**: Standardize 401→redirect and 403→error handling
- [ ] **M2.5**: Add cross-SPA session compatibility testing
- [ ] **M2.6**: Update all Admin Panel stores to use centralized client

#### Acceptance Criteria:
- Both SPAs use `access_token` localStorage key
- Admin Panel has automated auth headers
- Consistent error handling across SPAs
- Cross-SPA session sharing works

#### Files to Modify:
```
app/frontend/web/src/stores/auth.js
app/frontend/web/src/api/pdp.js
app/frontend/panel/src/api/client.js (new)
app/frontend/panel/src/stores/auth.js
app/frontend/panel/src/stores/*.js (all stores)
```

### Week 5: Policy Exposure
**Owner**: Backend Team  
**Deliverables**: Configuration endpoints, admin policy viewer

#### Tasks:
- [ ] **M3.1**: Create `/api/v1/auth/config` endpoint
- [ ] **M3.2**: Implement read-only policy display in admin panel
- [ ] **M3.3**: Add authentication configuration viewer component
- [ ] **M3.4**: Restrict config endpoint to admin-only access
- [ ] **M3.5**: Add configuration validation and monitoring

#### Acceptance Criteria:
- Config endpoint returns current JWT settings
- Admin panel displays authentication policies
- Configuration changes are logged and audited

#### Files to Create/Modify:
```
app/api/routers/auth.py (new)
app/frontend/panel/src/views/AuthConfig.vue (new)
app/frontend/panel/src/components/auth/PolicyViewer.vue (new)
```

### Week 6-7: Admin Panel Integration
**Owner**: Frontend Team  
**Deliverables**: Authentication monitoring dashboard

#### Tasks:
- [ ] **M4.1**: Create authentication overview dashboard
- [ ] **M4.2**: Implement metrics widgets (success rate, error rate, latency)
- [ ] **M4.3**: Build audit log viewer with filtering
- [ ] **M4.4**: Add token analytics and decode failure tracking
- [ ] **M4.5**: Create authentication health monitoring
- [ ] **M4.6**: Implement real-time metrics updates

#### Acceptance Criteria:
- Dashboard shows auth success/error rates
- Audit logs display with PII masking
- Token analytics show decode patterns
- Real-time updates every 30 seconds

#### Files to Create:
```
app/frontend/panel/src/views/AuthDashboard.vue
app/frontend/panel/src/components/auth/MetricsWidget.vue
app/frontend/panel/src/components/auth/AuditLogViewer.vue
app/frontend/panel/src/components/auth/TokenAnalytics.vue
app/api/routers/auth_admin.py
```

### Week 8: Migration Cutover
**Owner**: Full Team  
**Deliverables**: Legacy support removal, validation cleanup

#### Tasks:
- [ ] **M5.1**: Remove secondary JWT library imports
- [ ] **M5.2**: Remove legacy `sub=username` validation
- [ ] **M5.3**: Remove `auth_token` storage key support
- [ ] **M5.4**: Validate end-to-end authentication flows
- [ ] **M5.5**: Deploy to staging environment
- [ ] **M5.6**: Run comprehensive smoke tests

#### Acceptance Criteria:
- Zero JWT decode mismatches in logs
- Single JWT library in codebase
- All auth flows use canonical format
- Staging tests pass completely

## 📅 Phase 2: Dual Login & Telegram SSO (Weeks 9-16)

### Week 9-10: OTP Backend Infrastructure
**Owner**: Backend Team  
**Deliverables**: Phone authentication system

#### Tasks:
- [ ] **E1.1**: Create `otp_codes` database table
- [ ] **E1.2**: Implement OTP generation and hashing service
- [ ] **E1.3**: Integrate with existing Melipayamak SMS service
- [ ] **E1.4**: Create OTP verification and validation logic
- [ ] **E1.5**: Implement rate limiting for OTP requests
- [ ] **E1.6**: Add OTP cleanup and expiration handling
- [ ] **E1.7**: Create phone authentication API endpoints

#### API Endpoints:
```
POST /api/v1/auth/login/phone/request
POST /api/v1/auth/login/phone/verify
POST /api/v1/auth/phone/verify/request
POST /api/v1/auth/phone/verify/confirm
```

#### Acceptance Criteria:
- OTP delivery success rate ≥95%
- Verification response time p95 < 2 seconds
- Rate limiting blocks abuse attempts
- Zero plain-text OTP storage

#### Files to Create/Modify:
```
app/models/otp_models.py (new)
app/services/otp_service.py (new)
app/api/routers/auth_phone.py (new)
app/core/config.py (OTP settings)
```

### Week 11-12: Telegram Linking Infrastructure
**Owner**: Backend Team  
**Deliverables**: Web ↔ Bot account linking

#### Tasks:
- [ ] **E2.1**: Add Telegram fields to users table
- [ ] **E2.2**: Create `link_tokens` table for secure linking
- [ ] **E2.3**: Implement link token generation with nonces
- [ ] **E2.4**: Create Telegram linking API endpoints
- [ ] **E2.5**: Add single-use token enforcement
- [ ] **E2.6**: Implement bidirectional linking flows
- [ ] **E2.7**: Add Telegram account unlinking functionality

#### API Endpoints:
```
POST /api/v1/auth/telegram/link/request
POST /api/v1/auth/telegram/link/verify
POST /api/v1/auth/telegram/login/request
POST /api/v1/auth/telegram/login/verify
DELETE /api/v1/auth/telegram/unlink
```

#### Acceptance Criteria:
- Link success rate ≥99%
- Zero token replay attempts
- 3-minute token TTL enforced
- Cross-platform user recognition

#### Files to Create/Modify:
```
app/models/telegram_models.py (new)
app/services/telegram_service.py (new)
app/api/routers/auth_telegram.py (new)
app/db/models.py (user table extensions)
```

### Week 13-14: Frontend Extensions
**Owner**: Frontend Team  
**Deliverables**: Phone login UI, Telegram management

#### Tasks:
- [ ] **E3.1**: Create phone login form with international formatting
- [ ] **E3.2**: Build OTP verification view with countdown timer
- [ ] **E3.3**: Implement resend OTP functionality with cooldown
- [ ] **E3.4**: Add Telegram link status display
- [ ] **E3.5**: Create account settings for Telegram management
- [ ] **E3.6**: Implement unified error handling for all auth methods
- [ ] **E3.7**: Add authentication method selector

#### Components:
```
PhoneLoginForm.vue
OTPVerificationView.vue
TelegramLinkCard.vue
AuthMethodSelector.vue
TelegramSettings.vue
```

#### Acceptance Criteria:
- Phone number formatting works correctly
- OTP input auto-advances on completion
- Resend cooldown displays accurately
- Telegram status reflects backend state

#### Files to Create:
```
app/frontend/web/src/components/auth/PhoneLoginForm.vue
app/frontend/web/src/components/auth/OTPVerificationView.vue
app/frontend/web/src/components/auth/TelegramLinkCard.vue
app/frontend/web/src/components/auth/AuthMethodSelector.vue
app/frontend/web/src/views/AccountSettings.vue
```

### Week 15: Security & Monitoring
**Owner**: DevOps + Backend Team  
**Deliverables**: Rate limiting, monitoring, alerts

#### Tasks:
- [ ] **E4.1**: Implement Nginx/Cloudflare rate limiting
- [ ] **E4.2**: Add CAPTCHA integration for failed attempts
- [ ] **E4.3**: Create authentication monitoring dashboard
- [ ] **E4.4**: Implement alert thresholds and notifications
- [ ] **E4.5**: Add SMS cost tracking and budget alerts
- [ ] **E4.6**: Create brute force detection system
- [ ] **E4.7**: Implement comprehensive audit logging

#### Rate Limits:
```yaml
otp_request: 3/hour per phone, 10/hour per IP
telegram_link: 5/day per user, 20/hour per IP
login_attempts: 10/15min per identifier
```

#### Acceptance Criteria:
- Rate limits prevent >90% of abuse attempts
- Account lockout activates within 1 second
- CAPTCHA blocks automated attacks >95%
- All security events are audited

#### Files to Create/Modify:
```
deployment/configs/nginx-rate-limiting.conf
app/services/security_service.py (new)
app/api/routers/auth_monitoring.py (new)
app/frontend/panel/src/views/SecurityDashboard.vue
```

### Week 16: Rollout & Validation
**Owner**: Full Team  
**Deliverables**: Production deployment, feature flags, testing

#### Tasks:
- [ ] **E5.1**: Implement feature flag infrastructure
- [ ] **E5.2**: Deploy to staging with comprehensive testing
- [ ] **E5.3**: Run E2E test matrix validation
- [ ] **E5.4**: Deploy to production with blue/green strategy
- [ ] **E5.5**: Enable features progressively (admin → 10% → 100%)
- [ ] **E5.6**: Monitor metrics and validate success criteria
- [ ] **E5.7**: Document operational procedures

#### Feature Flags:
```yaml
auth_phone_otp: false
telegram_account_linking: false
captcha_protection: false
sms_cost_alerts: true
```

#### Acceptance Criteria:
- All E2E tests pass in staging
- Production deployment successful
- Progressive rollout completed
- Monitoring dashboard operational

## 🧪 Testing Strategy

### Unit Tests
- JWT token creation and validation
- OTP generation and verification
- Rate limiting logic
- Security service functions

### Integration Tests
- API endpoint functionality
- Database operations
- SMS service integration
- Telegram bot integration

### E2E Tests
- Complete authentication flows
- Cross-SPA session sharing
- Phone login with OTP
- Telegram linking flows
- Error handling scenarios

### Performance Tests
- Login latency benchmarks
- OTP delivery timing
- Rate limiting effectiveness
- Database query performance

## 📊 Monitoring & KPIs

### Authentication Metrics
- Success rate: ≥99%
- Error rate: ≤1%
- Login latency p95: ≤500ms
- OTP delivery p95: ≤60s

### Security Metrics
- Rate limit effectiveness: >90%
- CAPTCHA success rate: >95%
- Token replay attempts: 0
- Audit event coverage: 100%

### Business Metrics
- SMS cost tracking
- User adoption rates
- Cross-platform usage
- Support ticket reduction

## 🚨 Risk Management

### High-Risk Items
1. **SMS Provider Downtime**: Mitigation with fallback to email auth
2. **Token Security**: Single-use enforcement with short TTL
3. **Rate Limit Bypass**: Multiple layers of protection
4. **Cross-Platform State**: Clear status indicators

### Medium-Risk Items
1. **User Experience Confusion**: Comprehensive error messages
2. **Performance Impact**: Caching and optimization
3. **Database Load**: Proper indexing and cleanup
4. **Feature Flag Complexity**: Simple boolean flags

### Low-Risk Items
1. **UI/UX Changes**: Incremental improvements
2. **Configuration Updates**: Environment-specific settings
3. **Documentation**: Living documentation updates

## 📋 Deliverables Checklist

### Phase 1 Deliverables
- [ ] Unified JWT authentication system
- [ ] Cross-SPA session compatibility
- [ ] Admin authentication dashboard
- [ ] Policy configuration viewer
- [ ] Comprehensive audit logging

### Phase 2 Deliverables
- [ ] Phone + OTP authentication
- [ ] Telegram account linking
- [ ] Security hardening
- [ ] Rate limiting and monitoring
- [ ] Production deployment

### Documentation Deliverables
- [ ] API documentation
- [ ] Admin user guide
- [ ] Security procedures
- [ ] Troubleshooting guide
- [ ] Operational runbooks

## 👥 Team Responsibilities

### Backend Team
- JWT library consolidation
- OTP and Telegram services
- API endpoint development
- Database schema changes
- Security implementation

### Frontend Team
- UI component development
- State management updates
- Error handling implementation
- Admin dashboard creation
- Cross-SPA compatibility

### DevOps Team
- Rate limiting configuration
- Monitoring setup
- Alert configuration
- Deployment automation
- Security hardening

### QA Team
- Test case development
- E2E test automation
- Performance testing
- Security testing
- User acceptance testing

## 📞 Communication Plan

### Daily Standups
- Progress updates
- Blockers and dependencies
- Risk identification
- Next day priorities

### Weekly Reviews
- Milestone progress
- Quality metrics
- Risk assessment
- Timeline adjustments

### Phase Gates
- Deliverable validation
- Stakeholder sign-off
- Go/no-go decisions
- Lessons learned

## 🎯 Success Metrics

### Technical Success
- Zero authentication system downtime
- All security requirements met
- Performance targets achieved
- Code quality standards maintained

### Business Success
- Improved user experience
- Reduced support tickets
- Enhanced security posture
- Operational efficiency gains

### Team Success
- Knowledge transfer completed
- Documentation comprehensive
- Processes established
- Future maintenance enabled

---

**Next Steps**: 
1. Review and approve this project breakdown
2. Assign team members to specific tasks
3. Set up project tracking (Jira/GitHub Projects)
4. Begin Phase 1, Week 1 tasks
5. Establish daily standup schedule

**Contact**: [Project Manager] for questions and updates

---

## 🔧 Improvements & Alignments

### 1. TTL & Rate-Limit Alignment
- OTP delivery target: **p95 ≤ 15s**
- OTP verification latency: **p95 ≤ 2s**
- OTP expiry TTL: **2–5 minutes**
- OTP request rate-limit: **max 5 requests / 30 min per phone**
- Resend cooldown: **60s**
- OTP verify attempts: **max 5 failures / 15 min**, lockout 30 min
- Login attempts: **10 / 15 min per IP**
- SMS daily budget: **300 SMS/day**, alert at 80%, hard stop at 100% (overrideable by flag)

### 2. Telegram Link Security Checklist
- Single-use link tokens
- Nonce + server-side state
- TTL 2–5 minutes
- Domain allowlist (web + bot)
- Deep-link querystring stripped from browser history after exchange
- Audit all link/unlink/replay events

### 3. Client Storage Policy
- MVP: **localStorage** with key `access_token`
- Future migration path: HttpOnly cookie + SameSite=Lax/Strict + CSRF protection
- Operational toggle via config flag `auth.frontend.storage`
- PII safety: tokens must never be logged or stored in analytics

### 4. Abuse Budget & Alerts
- Budget telemetry: `sms_sent`, `sms_failed`, `sms_cost_estimate`
- Alerting thresholds:
  - 80% of budget: warning
  - 100%: hard stop, ops override required

### 5. Dependency & Critical Path
| Task                       | Depends On            | Risk if Late                          |
|----------------------------|-----------------------|---------------------------------------|
| Backend JWT unification    | None (foundational)   | All downstream blocked                |
| Frontend storage unify     | Backend claim format  | Broken sessions across SPAs            |
| OTP verify endpoint        | JWT unification       | No usable phone login flow             |
| Telegram link token flows  | OTP + JWT unification | SSO blocked; bot QA blocked            |
| Admin panel metrics        | Logging pipelines     | No observability for rollout           |

### 6. E2E Test Matrix
| Scenario             | Steps                          | Expected Result                     | Metrics                |
|----------------------|--------------------------------|-------------------------------------|------------------------|
| Email login success  | valid creds → token            | 200 + token, stored in interceptor  | login p95 latency      |
| Phone login success  | request OTP → verify           | 200 + token, otp_sent/verified logs | OTP delivery p95 ≤15s  |
| OTP expired          | request → wait TTL+            | 400 OTP_EXPIRED                     | error logged           |
| OTP wrong x5         | 5 wrong codes                  | 429 LOCKOUT, lockout timer started  | lockout enforced       |
| Resend cooldown      | resend <60s                    | 429 RATE_LIMITED                    | cooldown respected     |
| Web→Bot link         | issue link → tap /start token  | 200 link success, audit entry        | link success ≥99%      |
| Replay link token    | reuse token                    | 400 TOKEN_REPLAY                    | replay=0 in logs       |
| Bot→Web login        | /login → deep-link → exchange  | 200 web session established         | end-to-end latency     |
| Unlink idempotent    | unlink twice                   | 200 both times, 2nd no-op            | audit entries correct  |

### 7. Go/No-Go Gates
- **Phase 1 Exit:** Single JWT library in use; zero decode mismatches; SPA login/logout works both sides
- **Phase 2 Exit:** OTP success rate ≥95%; OTP delivery p95 ≤15s; failure spikes <5%
- **Phase 3 Exit:** Telegram linking success ≥99%; zero token replays; audit logs visible in panel

### 8. Assumptions & Non-Goals
- Out of scope for MVP: enterprise SSO (SAML/OIDC), passwordless magic-link, multi-factor auth
- Future backlog only: cookie-based storage migration, refresh tokens, multi-telegram accounts

### 9. Ownership & RACI
| Area     | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Backend  | BE Lead     | CTO         | Security  | QA       |
| Web      | Web Lead    | CTO         | UX        | QA       |
| Admin    | FE Lead     | PM          | Security  | QA       |
| Bot      | Bot Dev     | BE Lead     | PM        | QA       |
| DevOps   | DevOps Lead | CTO         | Security  | QA       |

### 10. Operational Runbooks
- Deliverable by Week 16: runbooks for auth incidents
- Include: high OTP failure rate, SMS provider outage, replay detection, JWT lib mismatch, bot link abuse
- Runbooks must specify: detection signal, escalation chain, mitigation steps, rollback path
