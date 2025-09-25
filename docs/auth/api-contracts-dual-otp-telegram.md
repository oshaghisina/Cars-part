# API Contracts: Dual Login & Telegram SSO

## 1. Endpoint Contracts

### POST /api/v1/auth/login/email
**Description**: Authenticate user with email and password

**Request Schema**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "user",
    "phone_verified": false,
    "telegram_linked": false
  }
}
```

**Response 401**:
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid email or password",
  "details": {
    "attempts_remaining": 2,
    "lockout_duration": null
  }
}
```

**Response 429**:
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many login attempts",
  "details": {
    "retry_after": 300,
    "lockout_until": "2024-01-15T10:30:00Z"
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No

---

### POST /api/v1/auth/login/phone/request
**Description**: Request OTP for phone number authentication

**Request Schema**:
```json
{
  "phone_number": "+989123456789"
}
```

**Response 200**:
```json
{
  "message": "OTP sent successfully",
  "expires_in": 300,
  "resend_available_in": 60,
  "attempts_remaining": 3
}
```

**Response 429**:
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many OTP requests",
  "details": {
    "retry_after": 1800,
    "daily_limit_reached": false
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No

---

### POST /api/v1/auth/login/phone/verify
**Description**: Verify OTP and issue access token

**Request Schema**:
```json
{
  "phone_number": "+989123456789",
  "otp_code": "123456"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 123,
    "phone": "+989123456789",
    "role": "user",
    "phone_verified": true,
    "telegram_linked": false
  }
}
```

**Response 400**:
```json
{
  "error": "OTP_INVALID",
  "message": "Invalid or expired OTP code",
  "details": {
    "attempts_remaining": 2,
    "can_resend": true
  }
}
```

**Response 400**:
```json
{
  "error": "OTP_EXPIRED", 
  "message": "OTP code has expired",
  "details": {
    "expired_at": "2024-01-15T10:25:00Z",
    "can_request_new": true
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No

---

### POST /api/v1/auth/phone/verify/request
**Description**: Send OTP for phone number verification (account binding)

**Request Schema**:
```json
{
  "phone_number": "+989123456789"
}
```

**Response 200**:
```json
{
  "message": "Verification OTP sent",
  "expires_in": 300,
  "phone_number": "+989123456789"
}
```

**Headers**: Content-Type: application/json, Authorization: Bearer <token>  
**Auth Required**: Yes (authenticated user)

---

### POST /api/v1/auth/phone/verify/confirm
**Description**: Confirm phone number verification with OTP

**Request Schema**:
```json
{
  "phone_number": "+989123456789",
  "otp_code": "123456"
}
```

**Response 200**:
```json
{
  "verified": true,
  "phone_number": "+989123456789",
  "verified_at": "2024-01-15T10:30:00Z"
}
```

**Headers**: Content-Type: application/json, Authorization: Bearer <token>  
**Auth Required**: Yes (authenticated user)

---

### POST /api/v1/auth/telegram/link/request
**Description**: Generate link token for Telegram account linking (Web → Bot)

**Request Schema**:
```json
{}
```

**Response 200**:
```json
{
  "link_token": "abc123def456ghi789jkl012mno345pqr678",
  "deep_link_url": "https://t.me/YourBot?start=abc123def456ghi789jkl012mno345pqr678",
  "expires_in": 180,
  "instructions": "Click the link to connect your Telegram account"
}
```

**Response 409**:
```json
{
  "error": "ALREADY_LINKED",
  "message": "Telegram account already linked",
  "details": {
    "telegram_username": "@existing_user",
    "linked_at": "2024-01-10T15:20:00Z"
  }
}
```

**Headers**: Content-Type: application/json, Authorization: Bearer <token>  
**Auth Required**: Yes (authenticated user)

---

### POST /api/v1/auth/telegram/link/verify
**Description**: Verify link token and establish Telegram account connection

**Request Schema**:
```json
{
  "link_token": "abc123def456ghi789jkl012mno345pqr678",
  "telegram_user_id": 123456789,
  "telegram_username": "user123",
  "telegram_first_name": "John"
}
```

**Response 200**:
```json
{
  "success": true,
  "user": {
    "id": 123,
    "name": "John Doe",
    "role": "user"
  },
  "linked_at": "2024-01-15T10:30:00Z"
}
```

**Response 400**:
```json
{
  "error": "TOKEN_REPLAY",
  "message": "Link token has already been used",
  "details": {
    "used_at": "2024-01-15T10:25:00Z"
  }
}
```

**Response 409**:
```json
{
  "error": "TELEGRAM_ALREADY_LINKED",
  "message": "This Telegram account is linked to another user",
  "details": {
    "linked_user_id": 456
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No (bot-initiated)

---

### POST /api/v1/auth/telegram/login/request
**Description**: Generate web login token for linked Telegram user

**Request Schema**:
```json
{
  "telegram_user_id": 123456789
}
```

**Response 200**:
```json
{
  "login_token": "xyz789uvw456rst123abc890def567ghi234",
  "web_login_url": "https://example.com/auth/telegram?token=xyz789uvw456rst123abc890def567ghi234",
  "expires_in": 180
}
```

**Response 404**:
```json
{
  "error": "TELEGRAM_NOT_LINKED",
  "message": "Telegram account not linked to any user",
  "details": {
    "telegram_user_id": 123456789
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No (bot-initiated)

---

### POST /api/v1/auth/telegram/login/verify
**Description**: Exchange login token for access token (Bot → Web)

**Request Schema**:
```json
{
  "login_token": "xyz789uvw456rst123abc890def567ghi234"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer", 
  "expires_in": 1800,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "user",
    "telegram_linked": true,
    "telegram_username": "user123"
  }
}
```

**Response 400**:
```json
{
  "error": "TOKEN_EXPIRED",
  "message": "Login token has expired",
  "details": {
    "expired_at": "2024-01-15T10:33:00Z"
  }
}
```

**Headers**: Content-Type: application/json  
**Auth Required**: No

---

### DELETE /api/v1/auth/telegram/unlink
**Description**: Disconnect Telegram account from user profile

**Request Schema**:
```json
{}
```

**Response 200**:
```json
{
  "success": true,
  "message": "Telegram account disconnected",
  "unlinked_at": "2024-01-15T10:30:00Z"
}
```

**Response 200** (Idempotent):
```json
{
  "success": true,
  "message": "No Telegram account was linked",
  "details": {
    "was_linked": false
  }
}
```

**Headers**: Content-Type: application/json, Authorization: Bearer <token>  
**Auth Required**: Yes (authenticated user)

## 2. DB Migration DDL (Finalized Sketches)

### Users Table Extensions
```sql
-- Add dual login and Telegram fields to existing users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS:
  phone VARCHAR(20) NULL,                    -- E.164 format phone number
  phone_verified_at TIMESTAMP NULL,          -- Phone verification timestamp  
  telegram_user_id BIGINT NULL UNIQUE,      -- Telegram user identifier
  telegram_username VARCHAR(50) NULL,        -- Telegram @username for display
  telegram_first_name VARCHAR(50) NULL,      -- Telegram first name
  telegram_last_name VARCHAR(50) NULL,       -- Telegram last name  
  telegram_linked_at TIMESTAMP NULL,         -- Account linking timestamp
  last_login_method VARCHAR(20) NULL;        -- 'email'|'phone'|'telegram'

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_users_login_method ON users(last_login_method);
```

### OTP Codes Table
```sql
-- Table for storing hashed OTP codes
CREATE TABLE IF NOT EXISTS otp_codes (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(20) NOT NULL,         -- E.164 format
  user_id INTEGER NULL REFERENCES users(id), -- NULL for verification flows
  code_hash VARCHAR(64) NOT NULL,            -- SHA-256 hashed OTP
  code_type VARCHAR(20) NOT NULL,            -- 'login'|'verification'
  attempts INTEGER DEFAULT 0,                -- Failed validation attempts
  expires_at TIMESTAMP NOT NULL,             -- 5-minute expiry from creation
  used_at TIMESTAMP NULL,                    -- Consumption timestamp
  created_at TIMESTAMP DEFAULT NOW(),
  ip_address_hash VARCHAR(64) NULL           -- Rate limiting by IP
);

-- Indexes for performance and cleanup
CREATE INDEX idx_otp_phone_expiry ON otp_codes(phone_number, expires_at);
CREATE INDEX idx_otp_cleanup ON otp_codes(expires_at);
CREATE INDEX idx_otp_user_type ON otp_codes(user_id, code_type);
```

### Link Tokens Table
```sql
-- Table for Telegram linking tokens
CREATE TABLE IF NOT EXISTS link_tokens (
  id SERIAL PRIMARY KEY,
  token_hash VARCHAR(64) NOT NULL UNIQUE,    -- SHA-256 hashed token
  token_type VARCHAR(20) NOT NULL,           -- 'web_to_bot'|'bot_to_web'
  nonce VARCHAR(32) NOT NULL,                -- Cryptographic nonce
  user_id INTEGER NULL REFERENCES users(id), -- Set for web_to_bot
  telegram_user_id BIGINT NULL,              -- Set for bot_to_web
  expires_at TIMESTAMP NOT NULL,             -- 3-minute expiry
  used_at TIMESTAMP NULL,                    -- Consumption timestamp
  created_at TIMESTAMP DEFAULT NOW(),
  ip_address_hash VARCHAR(64) NULL           -- Rate limiting
);

-- Indexes for performance and security
CREATE INDEX idx_link_tokens_hash ON link_tokens(token_hash);
CREATE INDEX idx_link_tokens_expiry ON link_tokens(expires_at);
CREATE INDEX idx_link_tokens_telegram ON link_tokens(telegram_user_id);
CREATE INDEX idx_link_tokens_user ON link_tokens(user_id);
```

### Retention & Cleanup
```sql
-- Automated cleanup for expired tokens (scheduled job)
DELETE FROM otp_codes WHERE expires_at < NOW() - INTERVAL '24 hours';
DELETE FROM link_tokens WHERE expires_at < NOW() - INTERVAL '1 hour';

-- Audit trail cleanup (separate retention policy)
-- Note: Audit events maintained in audit_logs table with 90-day retention
```

## 3. Rate Limits & Feature Flags

### Rate Limiting Configuration
```yaml
rate_limits:
  otp_request:
    per_phone: "3 requests per hour"        # Per phone number
    per_ip: "10 requests per hour"          # Per IP address
    resend_cooldown: "60 seconds"           # Between resend attempts
  
  otp_verify:
    per_phone: "10 attempts per 15 minutes" # OTP validation attempts
    lockout_threshold: 5                    # Failed attempts trigger lockout
    lockout_duration: "30 minutes"         # Account lockout period
  
  telegram_link:
    per_user: "5 attempts per day"          # Link token generation
    per_ip: "20 attempts per hour"          # IP-based limiting
    per_telegram: "3 attempts per hour"     # Per Telegram user ID
  
  phone_verification:
    per_user: "3 requests per hour"         # Account phone verification
    per_ip: "10 requests per hour"          # IP-based limiting
```

### Feature Flags
```yaml
features:
  auth_phone_otp: false                     # Enable phone + OTP authentication
  auth_phone_verification: false           # Enable account phone verification
  telegram_account_linking: false          # Enable web ↔ bot linking  
  telegram_web_login: false                # Enable bot → web login flow
  otp_voice_fallback: false                # Future: voice OTP delivery
  captcha_protection: false                # CAPTCHA after failed attempts
  sms_cost_alerts: true                    # Budget monitoring alerts
```

## 4. Security Implementation Notes

### Token Security
- **OTP Hashing**: SHA-256 with application-wide salt, never store plain text codes
- **Link Token Hashing**: SHA-256 with unique salt per token, 32-character base entropy
- **Cryptographic Nonce**: Server-generated randomness for replay protection
- **Single-Use Enforcement**: Mark `used_at` timestamp after successful validation

### Time-to-Live Policies
- **OTP Codes**: 5 minutes maximum lifespan from generation
- **Link Tokens**: 3 minutes maximum lifespan (shorter for security)
- **Verification OTP**: 5 minutes for account phone binding
- **Access Tokens**: 30 minutes (consistent with main authentication)

### Deep Link Security
- **HTTPS-Only**: All web login deep links must use HTTPS protocol
- **Domain Allowlist**: Validate origin domains for token redemption
- **URL Parameter Cleanup**: Remove tokens from browser history after consumption
- **Referrer Policy**: Strict policy to prevent token leakage

### Audit Events
```json
// Example audit event structure
{
  "event_type": "otp_requested|otp_verified|telegram_linked|telegram_unlinked",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 123,
  "phone_hash": "sha256_hash",               // Phone number hashed
  "ip_hash": "sha256_hash",                  // IP address hashed
  "telegram_user_id": 123456789,             // Telegram user ID (not hashed)
  "success": true,
  "error_code": null,
  "metadata": {
    "attempts": 1,
    "method": "sms",
    "provider": "melipayamak"
  }
}
```

## 5. Test Matrix (E2E)

### Success Flows
| Test Case | Steps | Expected Response | Validation |
|-----------|-------|-------------------|------------|
| **Email login** | POST /auth/login/email with valid creds | 200 + access_token | Token validates, user authenticated |
| **Phone OTP request** | POST /auth/login/phone/request | 200 + "OTP sent" | SMS delivered within 30s |
| **Phone OTP verify** | POST /auth/login/phone/verify with valid code | 200 + access_token | Token validates, user authenticated |
| **Phone verification** | Request → Verify OTP for account | 200 + verified=true | user.phone_verified_at updated |
| **Web→Bot link** | Generate link token → Bot verify | 200 + success=true | telegram_user_id linked to user |
| **Bot→Web login** | Generate login token → Web exchange | 200 + access_token | Web session established |
| **Telegram unlink** | DELETE /auth/telegram/unlink | 200 + success=true | telegram_user_id cleared |

### Failure Flows  
| Test Case | Steps | Expected Response | Validation |
|-----------|-------|-------------------|------------|
| **Invalid email/password** | POST /auth/login/email with wrong creds | 401 INVALID_CREDENTIALS | Attempts tracked |
| **OTP expired** | Wait >5min, then verify OTP | 400 OTP_EXPIRED | Expired code rejected |
| **OTP wrong code** | Verify with incorrect 6-digit code | 400 OTP_INVALID | Attempts incremented |
| **Rate limit OTP** | >3 requests per hour per phone | 429 RATE_LIMITED | Cooldown enforced |
| **Rate limit verify** | >5 wrong OTP attempts | 429 LOCKOUT | 30min lockout applied |
| **Link token replay** | Use same link token twice | 400 TOKEN_REPLAY | Second use rejected |
| **Telegram already linked** | Link when telegram_user_id exists | 409 TELEGRAM_ALREADY_LINKED | Error with existing user |
| **Login token expired** | Use login token >3min old | 400 TOKEN_EXPIRED | Expired token rejected |
| **Unlink not linked** | Unlink when no Telegram linked | 200 + was_linked=false | Idempotent success |

### Rate Limiting Tests
| Test Case | Steps | Expected Response | Validation |
|-----------|-------|-------------------|------------|
| **IP rate limit** | >10 OTP requests per hour from IP | 429 RATE_LIMITED | IP blocked temporarily |
| **Phone rate limit** | >3 OTP requests per hour per phone | 429 RATE_LIMITED | Phone blocked temporarily |
| **Resend cooldown** | Request resend <60s after previous | 429 RATE_LIMITED | Cooldown enforced |
| **Daily SMS limit** | Reach daily SMS budget cap | 503 SERVICE_UNAVAILABLE | Feature flag auto-disable |

## 6. Error Code Reference

### Authentication Errors
- **INVALID_CREDENTIALS**: Wrong email/password combination
- **ACCOUNT_LOCKED**: Temporary lockout after failed attempts
- **RATE_LIMITED**: Too many requests within time window
- **USER_NOT_FOUND**: Email/phone not associated with account

### OTP Errors  
- **OTP_INVALID**: Wrong OTP code provided
- **OTP_EXPIRED**: OTP code past expiration time
- **OTP_ALREADY_USED**: Attempt to reuse consumed OTP
- **OTP_MAX_ATTEMPTS**: Exceeded validation attempt limit

### Telegram Errors
- **TOKEN_REPLAY**: Attempt to reuse consumed link/login token
- **TOKEN_EXPIRED**: Token past expiration time
- **ALREADY_LINKED**: User account already has Telegram linked
- **TELEGRAM_ALREADY_LINKED**: Telegram account linked to different user
- **TELEGRAM_NOT_LINKED**: Telegram user not associated with any account

### System Errors
- **SERVICE_UNAVAILABLE**: SMS service temporarily disabled
- **PROVIDER_ERROR**: SMS delivery provider failure
- **INVALID_PHONE_FORMAT**: Phone number format validation failed

## 7. Open Questions

1. **OTP Configuration Finalization**: Confirm 6-digit OTP codes with 5-minute expiry, or adjust to 4-digit codes with 3-minute expiry for faster mobile UX?

2. **SMS Fallback Strategy**: Should voice OTP delivery be implemented as automatic fallback when SMS fails, or user-requested alternative with separate rate limits?

3. **Link Token TTL Policy**: Confirm 3-minute expiry for link tokens, or extend to 5 minutes to accommodate slower mobile app switching and user decision time?

4. **Multiple Telegram Account Support**: Maintain strict 1:1 Telegram-to-user mapping, or allow multiple Telegram accounts per user with separate account_links table?

5. **Localization Implementation**: Should error messages and SMS templates support automatic Persian/English detection based on phone number country code or user preference?

6. **Cookie Migration Timeline**: When should migration from localStorage to HttpOnly cookies be prioritized, and what triggers warrant the additional CSRF implementation complexity?

7. **SMS Provider Redundancy**: Should secondary SMS provider integration be included in MVP scope, or deferred to future iteration with queued retry logic?

8. **CAPTCHA Integration Point**: Should CAPTCHA be required after 2 failed OTP attempts (aggressive) or 5 failed attempts (permissive), and should it apply to both email and phone authentication?
