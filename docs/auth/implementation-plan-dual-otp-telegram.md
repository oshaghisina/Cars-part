# Implementation Plan: Dual Login & Telegram SSO Extensions

## 1. Epics & Tasks

### E1: OTP Backend Infrastructure
**Duration**: 2 weeks  
**Dependencies**: Existing SMS service (Melipayamak integration)

#### Database Schema
```sql
-- OTP Codes Table (DDL Sketch)
CREATE TABLE otp_codes (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,  -- E.164 format
    user_id INTEGER REFERENCES users(id),  -- NULL for verification flows
    code_hash VARCHAR(64) NOT NULL,     -- SHA-256 with salt
    code_type VARCHAR(20) NOT NULL,     -- 'login' | 'verification'
    attempts INTEGER DEFAULT 0,         -- Failed validation attempts
    expires_at TIMESTAMP NOT NULL,      -- 5-minute expiry
    used_at TIMESTAMP NULL,             -- Consumption timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    ip_address_hash VARCHAR(64),        -- Rate limiting
    INDEX idx_phone_expiry (phone_number, expires_at),
    INDEX idx_cleanup (expires_at)      -- Auto-cleanup expired codes
);
```

#### Services Implementation
- **OTPService.generate()**: Create 6-digit code, hash with salt, store with expiry
- **OTPService.send()**: Provider adapter pattern for Melipayamak, extensible for voice/email
- **OTPService.verify()**: Hash comparison, attempt tracking, expiry validation, single-use enforcement
- **OTPService.cleanup()**: Background task for expired code removal

#### API Endpoints
- **POST /api/v1/auth/phone/request**: Generate and send OTP (rate limited: 3/hour per phone)
- **POST /api/v1/auth/phone/verify**: Validate OTP and issue access token (rate limited: 10/min per IP)
- **POST /api/v1/auth/phone/verification/request**: Send verification OTP for account phone binding
- **POST /api/v1/auth/phone/verification/confirm**: Confirm phone ownership for account

#### Audit Events
- **otp_requested**: Phone number (hashed), IP (hashed), success/failure, rate limit status
- **otp_verified**: Code validation outcome, attempt count, user authentication result
- **otp_failed**: Failed validation attempts, lockout triggers, abuse detection events

### E2: Telegram Linking Infrastructure
**Duration**: 2 weeks  
**Dependencies**: Telegram Bot API integration

#### Database Schema Extensions
```sql
-- User table additions
ALTER TABLE users ADD COLUMN:
    telegram_user_id BIGINT UNIQUE NULL,
    telegram_username VARCHAR(50) NULL,
    telegram_first_name VARCHAR(50) NULL,
    telegram_linked_at TIMESTAMP NULL;

-- Short-lived tokens for linking
CREATE TABLE link_tokens (
    id SERIAL PRIMARY KEY,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    token_type VARCHAR(20) NOT NULL,    -- 'web_to_bot' | 'bot_to_web'
    nonce VARCHAR(32) NOT NULL,         -- Cryptographic nonce
    user_id INTEGER REFERENCES users(id),
    telegram_user_id BIGINT,
    expires_at TIMESTAMP NOT NULL,      -- 3-minute expiry
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    ip_address_hash VARCHAR(64),
    INDEX idx_token_expiry (expires_at),
    INDEX idx_telegram_user (telegram_user_id)
);
```

#### API Endpoints
- **POST /api/v1/auth/telegram/link/request**: Generate link token for authenticated web user
- **POST /api/v1/auth/telegram/link/verify**: Bot verification of link token with telegram_user_id
- **POST /api/v1/auth/telegram/login/request**: Bot requests web login token for linked user
- **POST /api/v1/auth/telegram/login/verify**: Web exchanges login token for access token
- **DELETE /api/v1/auth/telegram/unlink**: Disconnect Telegram account from user profile

#### Bot Integration Points
- **Handler: /start <token>**: Process web→bot linking with token validation
- **Handler: /login**: Generate bot→web login flow with deep link
- **Handler: /unlink**: User-initiated account disconnection
- **Context Storage**: Maintain linking state during multi-step flows

### E3: Frontend Web Extensions
**Duration**: 2 weeks  
**Dependencies**: Unified auth store (from main implementation plan)

#### Authentication UI Components
- **PhoneLoginForm.vue**: Phone number input with international formatting and validation
- **OTPVerificationView.vue**: 6-digit code input with resend functionality and countdown timer
- **TelegramLinkCard.vue**: Account settings component for Telegram connection status
- **AuthMethodSelector.vue**: Toggle between email/password and phone/OTP authentication

#### Auth Store Extensions
- **Phone Actions**: `loginWithPhone()`, `requestOTP()`, `verifyOTP()`, `resendOTP()`
- **Telegram Actions**: `requestTelegramLink()`, `verifyTelegramLogin()`, `unlinkTelegram()`
- **State Management**: OTP request status, resend cooldowns, linking progress tracking
- **Error Handling**: Unified error states for rate limiting, invalid codes, expired tokens

#### Account Management Interface
- **Settings Integration**: Telegram link status display in user profile
- **Security Section**: Connected services overview with last activity timestamps
- **Unlinking Flow**: Confirmation dialog with security implications explanation

### E4: Telegram Bot UX
**Duration**: 1 week  
**Dependencies**: Bot framework integration, deep link configuration

#### Linking Flow Messages
- **Link Success**: "✅ Account successfully linked! I can now help you with orders and product searches."
- **Link Failure**: "❌ Connection failed. Please try again or contact support if the issue persists."
- **Already Linked**: "⚠️ This Telegram account is already connected to another user. Please unlink first."
- **Expired Token**: "⏰ This connection link has expired. Please request a new link from the web portal."

#### Login Flow Implementation
- **Login Command**: `/login` → generates web portal deep link with login token
- **Deep Link Format**: `https://example.com/auth/telegram?token=<login_token>`
- **Success Confirmation**: "🔗 Login link sent! Tap the link below to access your account in the web portal."
- **Error States**: Rate limited, user not linked, token generation failure handling

### E5: Security & Rate Limiting
**Duration**: 1 week  
**Dependencies**: Infrastructure configuration (Nginx/Cloudflare)

#### Rate Limiting Implementation
```yaml
# Example Nginx/Cloudflare configuration
rate_limits:
  otp_request:
    per_phone: "3 requests per hour"
    per_ip: "10 requests per hour"
  telegram_link:
    per_user: "5 attempts per day"
    per_ip: "20 attempts per hour"
  login_attempts:
    per_identifier: "10 attempts per 15 minutes"
    progressive_delay: "exponential backoff"
```

#### Lockout & Protection Rules
- **Account Lockout**: 3 failed OTP attempts = 30-minute phone number lockout
- **IP Blocking**: 50 failed attempts from single IP = 1-hour temporary block
- **CAPTCHA Trigger**: After 2 failed OTP attempts or 5 failed login attempts
- **Abuse Detection**: Automated pattern recognition for distributed attacks

### E6: Observability & Monitoring
**Duration**: 1 week  
**Dependencies**: Admin panel dashboard integration

#### Key Metrics
- **OTP Performance**: Request rate, delivery latency (p50/p95), verification success rate
- **Telegram Metrics**: Link success rate, bot→web login success rate, active linked accounts
- **Security Metrics**: Failed attempt rates, lockout frequency, abuse detection triggers
- **Cross-Platform Usage**: Authentication method distribution, user preference patterns

#### Alert Configuration
- **OTP Failure Spike**: >20% verification failure rate over 15-minute window
- **Token Replay Detection**: Any successful reuse of consumed link tokens
- **SMS Cost Alert**: Daily Melipayamak usage exceeding 80% of budget threshold
- **Brute Force Alert**: >100 failed attempts per hour across all authentication methods

#### Dashboard Integration
- **Authentication Overview**: Extend existing dashboard with dual login and Telegram metrics
- **Method Breakdown**: Pie chart showing email vs phone vs Telegram authentication distribution
- **Security Events**: Failed attempts, lockouts, and abuse detection in audit log view

### E7: Rollout & Backout Strategy
**Duration**: 1 week  
**Dependencies**: Feature flag infrastructure, staging environment

#### Feature Flag Configuration
```yaml
features:
  auth_phone_otp: false          # Enable phone + OTP authentication
  telegram_account_linking: false # Enable web ↔ bot linking
  otp_voice_fallback: false     # Future: voice OTP delivery
  captcha_protection: false     # CAPTCHA for failed attempts
```

#### Staging Validation Tests
- **Phone Login Flow**: Complete OTP request → SMS delivery → code verification → token issuance
- **Telegram Linking**: Web→Bot linking with token validation and Bot→Web login flow
- **Cross-Platform Recognition**: Verify same user context across web portal and Telegram bot
- **Security Validation**: Rate limiting, lockout behavior, token replay prevention

#### Production Deployment
- **Blue/Green Strategy**: Zero-downtime deployment with immediate rollback capability
- **Progressive Rollout**: Enable for admin users first, then 10% of users, then full rollout
- **Monitoring Dashboard**: Real-time metrics during rollout for immediate issue detection

#### Backout Procedures
- **Immediate Disable**: Feature flag toggle to disable new authentication methods
- **Token Invalidation**: Clear all pending OTP codes and link tokens from database
- **User Communication**: In-app notifications about temporary authentication method unavailability
- **Audit Preservation**: Maintain all authentication events for post-incident analysis

## 2. Acceptance Criteria per Epic

### E1: OTP Backend Infrastructure
- ✅ OTP verification response time p95 < 2 seconds
- ✅ SMS delivery success rate ≥95% within 30 seconds
- ✅ Zero plain-text OTP codes stored in database (all hashed)
- ✅ Rate limiting blocks exceed attempts with HTTP 429 responses
- ✅ Expired codes auto-cleaned within 24 hours of expiry

### E2: Telegram Linking Infrastructure  
- ✅ Link token TTL configurable between 2-5 minutes with 3-minute default
- ✅ Zero successful token replay attempts (single-use enforcement)
- ✅ Bidirectional linking success rate ≥99% for valid tokens
- ✅ Nonce uniqueness guaranteed (zero collisions in production)
- ✅ Cross-platform user context identical after successful linking

### E3: Frontend Web Extensions
- ✅ Phone login UI supports international phone number formatting
- ✅ OTP input auto-advances on 6-digit completion with paste support
- ✅ Resend cooldown timer displays accurate countdown (60-second intervals)
- ✅ Telegram link status accurately reflects backend connection state
- ✅ Unified error handling shows consistent messages for all authentication methods

### E4: Telegram Bot UX
- ✅ Deep links generate valid tokens 100% of the time when user is linked
- ✅ Bot messages support both English and Persian with proper Unicode handling
- ✅ Link/unlink flows complete within 30 seconds end-to-end
- ✅ Error messages provide actionable next steps for users

### E5: Security & Rate Limiting
- ✅ Rate limits prevent >90% of abuse attempts based on configured thresholds
- ✅ Account lockout activates within 1 second of threshold breach
- ✅ CAPTCHA integration blocks automated attacks with >95% effectiveness
- ✅ Audit events capture 100% of security-relevant authentication activities

### E6: Observability & Monitoring
- ✅ Authentication dashboard displays dual login metrics within 30-second refresh
- ✅ Alert system triggers within 2 minutes of threshold breach
- ✅ Audit log search supports filtering by authentication method and time range
- ✅ SMS cost tracking provides daily and monthly budget consumption visibility

## 3. Risks & Mitigations

### SMS Provider Reliability Risk
- **Risk**: Melipayamak service downtime or delivery delays affecting phone authentication
- **Mitigation**: Provider health monitoring, automatic fallback to email authentication, user notification of temporary unavailability

### SMS Cost Escalation Risk
- **Risk**: Automated abuse driving SMS costs beyond budget thresholds
- **Mitigation**: Daily budget limits, real-time cost monitoring, automatic feature disable at 90% budget consumption, CAPTCHA integration

### Token Security Risk
- **Risk**: Link token interception enabling unauthorized account access
- **Mitigation**: HTTPS-only deep links, single-use with immediate invalidation, 3-minute expiry, cryptographic nonces, audit all usage

### Telegram Bot Deep Link Abuse
- **Risk**: Malicious deep links attempting token replay or social engineering
- **Mitigation**: Server-side token validation, nonce verification, rate limiting per Telegram user, comprehensive audit logging

### Cross-Platform State Confusion
- **Risk**: Users uncertain about authentication status across web portal and bot
- **Mitigation**: Clear status indicators in both platforms, linking confirmation messages, account settings visibility

## 4. Timeline & Ownership

### Sprint Breakdown (3-4 Sprints)

#### Sprint 1: Backend Foundation (2 weeks)
- **E1**: OTP Backend Infrastructure
- **E2**: Telegram Linking Infrastructure  
- **Owner**: Backend Team
- **Deliverables**: Database schema, API endpoints, service layer

#### Sprint 2: Frontend Integration (2 weeks)
- **E3**: Frontend Web Extensions
- **E4**: Telegram Bot UX
- **Owner**: Frontend Team + Bot Developer
- **Deliverables**: Phone login UI, Telegram linking interface, bot handlers

#### Sprint 3: Security & Monitoring (2 weeks)
- **E5**: Security & Rate Limiting
- **E6**: Observability & Monitoring
- **Owner**: DevOps + Backend Team
- **Deliverables**: Rate limiting, monitoring dashboard, alert configuration

#### Sprint 4: Rollout & Validation (1 week)
- **E7**: Rollout & Backout Strategy
- **Owner**: Full Team
- **Deliverables**: Feature flags, staging tests, production deployment

### RACI Matrix

| Task | Backend | Frontend | Bot Dev | DevOps | QA |
|------|---------|----------|---------|--------|----|
| **OTP API Endpoints** | R,A | I | I | I | C |
| **Phone Login UI** | I | R,A | I | I | C |
| **Telegram Handlers** | I | I | R,A | I | C |
| **Rate Limiting** | C | I | I | R,A | C |
| **Monitoring Dashboard** | C | R,A | I | C | C |
| **Security Testing** | C | C | C | I | R,A |
| **Production Deployment** | C | C | C | R,A | C |

### Parallelizable Work
- **E1 & E2**: Backend infrastructure can be developed concurrently
- **E3 & E4**: Frontend web and bot UX can be built against mock APIs
- **E5 & E6**: Security and monitoring can be implemented while frontend development continues

### Sequential Dependencies
- **E3 depends on E1**: Frontend phone login requires OTP API endpoints
- **E4 depends on E2**: Bot UX requires Telegram linking API endpoints
- **E6 depends on E1,E2**: Monitoring requires backend metrics and events
- **E7 depends on all**: Rollout requires all components integrated and tested

## 5. Open Questions

1. **SMS Provider Redundancy**: Should we implement multi-provider SMS delivery (Melipayamak + backup) for critical OTP delivery, or maintain single provider with degraded service handling?

2. **OTP Localization Strategy**: Should SMS messages automatically use Persian for Iranian phone numbers and English for international numbers, or provide user language preference controls?

3. **Legal SMS Consent**: Do we need explicit SMS consent flows for OTP delivery to comply with Iranian telecommunications regulations, and what opt-out mechanisms are required?

4. **Telegram Bot Rate Limiting**: Should Telegram API rate limits be handled with queueing and retry logic, or immediate failure with user retry instructions?

5. **Cross-Platform Analytics**: Should user authentication method preferences be tracked for product analytics, and what privacy controls are needed for this data?

6. **Voice OTP Fallback**: What triggers should activate voice OTP delivery (SMS failure, user request, accessibility needs), and what cost thresholds are acceptable?

7. **Account Recovery Escalation**: When users lose access to both email and phone authentication methods, what manual verification process should support teams follow?

8. **Audit Data Retention**: Should dual login and Telegram linking events follow the same 90-day retention policy as web authentication, or require different compliance windows?

## E2E Test Matrix (MVP)

| Scenario | Steps | Expected | Metrics |
|----------|-------|----------|---------|
| **Email login success** | valid creds → token issued | 200 + token; interceptor stores | login latency p95 |
| **Phone login success** | request OTP → verify | 200 + token; metrics otp_sent/verified | OTP delivery p95 < 2s |
| **OTP expired** | request → wait TTL+ | 400 OTP_EXPIRED | error logged |
| **OTP wrong code x5** | 5 wrong attempts | 429 LOCKOUT | lockout duration applies |
| **Resend cooldown** | request → resend < cooldown | 429 RATE_LIMITED | cooldown enforced |
| **Link web→bot** | issue link token → tap start | link success; audit recorded | link success rate ≥99% |
| **Replay link token** | reuse same token | 400 TOKEN_REPLAY | replay=0 after fix |
| **Bot→web login** | /login → open link → exchange | web session established | end-to-end latency |
| **Unlink idempotent** | unlink twice | second = no-op success | audit logged |

## Risk Addendum
- User Experience risk: frequent expiry → ensure clear messages and quick retry; consider extending TTL if failure spikes.
- Provider downtime: add secondary SMS provider or queued retry with backoff.
- Localization errors: ensure FA/EN strings present before rollout; fallback to English with no crash.

## Ownership & RACI (Brief)
- Backend: OTP/link tokens, endpoints, audits — Owner: BE Lead
- Web: UI flows, interceptor, storage — Owner: Web Lead
- Bot: linking flows, messages — Owner: Bot Dev
- DevOps: rate-limits, monitors, alerts — Owner: DevOps
- QA: E2E matrix execution — Owner: QA
