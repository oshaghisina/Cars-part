# RFC: Authentication Extensions - Dual Login & Telegram SSO

## 1. Decision Summary

### Dual Authentication Methods
- **Adopt Email + Password**: Maintain existing credential-based authentication as primary method
- **Adopt Phone + OTP (SMS)**: Implement SMS-based one-time password authentication using existing Melipayamak integration
- **Unified Account Model**: Both methods authenticate to same user account with identical JWT tokens and role permissions

### Telegram Account Linking
- **Adopt Bidirectional Linking**: Support both Web→Bot and Bot→Web authentication flows
- **Short-lived Token Strategy**: Single-use, server-stored tokens with cryptographic nonces for secure account association
- **Cross-Platform Recognition**: Linked accounts maintain same permissions and profile data across web portal and Telegram bot

### Token Strategy Consistency
- **Access-Only JWT**: Maintain current access token approach without refresh tokens for MVP
- **Unified Claims Structure**: Same JWT format (`sub=user_id`, `role`, `exp`, `iat`) regardless of authentication method
- **Consistent TTL**: 30-minute access token lifespan across all authentication paths

## 2. Standards & Contracts

### JWT Token Standards
- **Claims Structure**: Unchanged from main RFC (`sub=user_id`, `role`, `exp`, `iat`)
- **Library Standard**: python-jose (consistent with main authentication RFC)
- **TTL Configuration**: 30 minutes (1800 seconds) for all authentication methods
- **Signing Algorithm**: HS256 with same secret key and validation logic

### Phone OTP Standards
- **Code Length**: 6 digits (numeric only for universal SMS compatibility)
- **Code Expiry**: 5 minutes from generation timestamp
- **Max Attempts**: 3 validation attempts per OTP before invalidation
- **Rate Limits**: 3 OTP requests per phone number per hour, 10 requests per IP per hour
- **Delivery Provider**: Melipayamak SMS service (existing integration)

### API Endpoints (Names Only, Non-binding)
```
Authentication Extensions:
POST /api/v1/auth/login/email          # Email + password authentication
POST /api/v1/auth/login/phone/request  # Request OTP for phone number
POST /api/v1/auth/login/phone/verify   # Verify OTP and issue access token
POST /api/v1/auth/phone/verify/request # Verify phone number for account
POST /api/v1/auth/phone/verify/confirm # Confirm phone verification OTP

Telegram Linking:
POST /api/v1/auth/telegram/link/request   # Web: Generate link token
POST /api/v1/auth/telegram/link/verify    # Bot: Verify link token
POST /api/v1/auth/telegram/login/request  # Bot: Generate web login token  
POST /api/v1/auth/telegram/login/verify   # Web: Exchange login token
POST /api/v1/auth/telegram/unlink        # Disconnect Telegram account
```

### Telegram Link Token Format
- **Type**: Opaque token (not JWT) for link-specific operations
- **Structure**: 32-character alphanumeric string with cryptographic randomness
- **Storage**: Server-side with nonce, user context, and expiration timestamp
- **Usage**: Single-use with immediate invalidation after verification
- **TTL**: 3 minutes from generation (shorter than OTP for security)

### Storage Policy & Migration
- MVP: localStorage with key `access_token`.
- Future migration path: HttpOnly cookies + CSRF; controlled via policy flag.
- Clients MUST never persist tokens in logs/analytics; redaction required.

## 3. Data Model Changes (Non-breaking)

### Enhanced User Fields
```sql
ALTER TABLE users ADD COLUMN:
- phone: VARCHAR(20) NULL                    # E.164 format phone number
- phone_verified_at: TIMESTAMP NULL          # Phone verification timestamp
- telegram_user_id: BIGINT NULL UNIQUE      # Telegram user identifier
- telegram_username: VARCHAR(50) NULL        # Telegram @username for display
- telegram_linked_at: TIMESTAMP NULL         # Account linking timestamp
- last_login_method: ENUM('email', 'phone', 'telegram') NULL
```

### OTP Codes Table
```sql
CREATE TABLE otp_codes:
- id: SERIAL PRIMARY KEY
- phone_number: VARCHAR(20) NOT NULL INDEX  # E.164 format
- user_id: INTEGER NULL REFERENCES users(id) # Null for verification, set for login
- code_hash: VARCHAR(64) NOT NULL           # SHA-256 hashed OTP
- code_type: ENUM('login', 'verification') NOT NULL
- attempts: INTEGER DEFAULT 0               # Failed validation attempts
- expires_at: TIMESTAMP NOT NULL INDEX      # 5-minute expiry
- used_at: TIMESTAMP NULL                   # Consumption timestamp
- created_at: TIMESTAMP DEFAULT NOW()
- ip_address_hash: VARCHAR(64)              # Rate limiting by IP
```

### Link Tokens Table
```sql
CREATE TABLE link_tokens:
- id: SERIAL PRIMARY KEY
- token_hash: VARCHAR(64) NOT NULL UNIQUE   # SHA-256 hashed token
- token_type: ENUM('web_to_bot', 'bot_to_web') NOT NULL
- nonce: VARCHAR(32) NOT NULL               # Cryptographic nonce
- user_id: INTEGER NULL REFERENCES users(id) # Set for web_to_bot
- telegram_user_id: BIGINT NULL             # Set for bot_to_web  
- expires_at: TIMESTAMP NOT NULL INDEX      # 3-minute expiry
- used_at: TIMESTAMP NULL                   # Consumption timestamp
- created_at: TIMESTAMP DEFAULT NOW()
- ip_address_hash: VARCHAR(64)              # Rate limiting
```

### Retention Policies
- **OTP Codes**: Auto-delete after 24 hours (beyond any practical expiry)
- **Link Tokens**: Auto-delete after 1 hour (well beyond 3-minute expiry)
- **User Linking History**: Maintain linking/unlinking events in audit log for 90 days

## 4. KPIs & Acceptance Criteria

### Phone Authentication Performance
- **OTP Delivery Success Rate**: ≥95% within 30 seconds using Melipayamak service
- **Phone Login Success Rate**: ≥99% for valid OTP codes submitted within expiry window
- **OTP Delivery Latency (p95)**: ≤60 seconds from request to SMS receipt
- **Phone Verification Success Rate**: ≥99% for account phone number verification flow

### Telegram Linking Performance  
- **Link Success Rate**: ≥99% for valid tokens used within expiry window
- **Bot→Web Login Success Rate**: ≥99% for valid login tokens exchanged within TTL
- **Link Token Generation Latency**: ≤200ms for link token creation and deep link generation
- **Cross-Platform Recognition**: 100% of linked accounts recognized in both web portal and Telegram bot

### Security Validation
- **Zero Token Replay**: No successful token reuse detected in audit logs after single-use enforcement
- **Rate Limit Effectiveness**: SMS abuse attempts blocked within configured thresholds
- **Audit Event Coverage**: 100% of authentication events logged (phone login, linking, unlinking)
- **Nonce Uniqueness**: Zero cryptographic nonce collisions in link token generation
- SMS cost alert fires at 80% of daily budget; hard-stop at 100% (feature-flag overrideable).
- UX KPI: after 401 (expired), user is redirected to login within ≤ 1s or shown a clear action.
- Replay attempts = 0 (no double-use of link tokens in logs).

## 5. Rollout & Backout Plan

### Rollout Strategy
1. **Dark Launch OTP Endpoints**: Deploy backend API endpoints with feature flag disabled
2. **SMS Integration Testing**: Validate OTP delivery using existing Melipayamak configuration
3. **Frontend Phone Login UI**: Deploy phone authentication interface with feature flag
4. **Telegram Link API**: Deploy linking endpoints with bot integration testing
5. **Progressive Enablement**: Enable features for admin users first, then general rollout

### Feature Flag Configuration
```yaml
features:
  phone_authentication: false    # Enable phone + OTP login
  telegram_linking: false        # Enable web ↔ bot account linking
  otp_fallback_voice: false     # Future: voice OTP delivery
  link_multiple_telegram: false  # Future: multiple Telegram accounts per user
```

### Backout Strategy
- **Immediate Flag Disable**: Turn off feature flags to revert to email-only authentication
- **Token Invalidation**: Clear all pending OTP codes and link tokens from database
- **UI Rollback**: Hide phone login and Telegram linking interfaces
- **Audit Preservation**: Maintain all authentication events for security analysis
- **Gradual Re-enable**: Phased re-activation with enhanced monitoring after issue resolution

## 6. Risks & Mitigations

### SMS Abuse & Cost Control
- **Risk**: Automated OTP requests causing SMS cost spikes and service abuse
- **Mitigation**: Per-IP rate limiting (10/hour), per-phone limiting (3/hour), CAPTCHA after 2 failed attempts, daily SMS budget alerts

### Token Replay & Security
- **Risk**: Intercepted link tokens used for unauthorized account access
- **Mitigation**: Single-use enforcement with server-side nonce validation, 3-minute expiry, HTTPS-only deep links, immediate invalidation

### UX Confusion & Support Load
- **Risk**: Users unable to complete phone authentication or Telegram linking flows
- **Mitigation**: Unified error messages, clear retry guidance, fallback to email authentication, comprehensive help documentation

### Cross-Platform State Confusion
- **Risk**: Users uncertain about authentication status across web portal and Telegram bot
- **Mitigation**: Clear linking status display, confirmation messages in both platforms, account settings showing connected services

### Telegram Bot Dependency
- **Risk**: Telegram API downtime affecting web authentication for linked users
- **Mitigation**: Telegram linking is additive only, web authentication remains functional independently, graceful degradation
- SMS abuse → per-IP/identifier rate-limit + captcha (feature-flag) + budget alerts.
- Token leakage in deep-links → short TTL + nonce + single-use + domain allowlist.

## 7. Integration Points

### SMS Service Extension
- **Template Integration**: Extend existing SMS template system for OTP delivery messages
- **Analytics Integration**: Include OTP delivery in existing SMS analytics and monitoring
- **Cost Tracking**: Monitor OTP-related SMS costs within existing Melipayamak budget management

### Telegram Bot Enhancement
- **Authentication Context**: Bot recognizes linked users and provides personalized responses
- **Order Integration**: Bot can access user's order history and provide status updates
- **Admin Notifications**: Bot can notify linked admin users of system events

### Admin Panel Integration
- **User Management**: Display linked Telegram accounts in user profile views
- **Authentication Analytics**: Include phone and Telegram authentication in existing metrics
- **Audit Integration**: Phone and linking events included in authentication audit logs

## 8. Open Questions

1. **OTP Code Configuration**: Should OTP codes be 4 digits (faster to type) or 6 digits (more secure), and should expiry be 3 minutes (security) or 5 minutes (usability)?

2. **SMS Provider Fallback**: Should we implement voice OTP delivery as fallback when SMS fails, and what cost thresholds warrant fallback activation?

3. **Link Token TTL Policy**: Should link tokens expire in 2 minutes (high security) or 5 minutes (better mobile app switching UX), and should failed attempts extend or reset the expiry?

4. **Multiple Telegram Support**: Should users be allowed to link multiple Telegram accounts to enable family sharing or business/personal separation?

5. **Localization Priority**: Should OTP SMS messages support both English and Persian with automatic language detection, or maintain single language for MVP simplicity?

6. **CAPTCHA Integration Threshold**: At what failed attempt count should CAPTCHA be required for phone authentication (after 2 attempts, 3 attempts, or IP-based triggering)?

7. **Cross-Platform Logout Policy**: Should logout from web portal automatically unlink Telegram account, or maintain independent session lifecycles with manual unlinking only?

8. **Deep Link Domain Strategy**: Should Telegram→Web login links use the same domain as the web portal, or separate authentication-specific subdomain for security isolation?
