# CORS Preflight Resolution Strategy

## 1. Executive Summary

The production admin panel at `http://5.223.41.154/panel/` is experiencing systematic CORS preflight failures that prevent authentication flows. The issue manifests as 400 Bad Request responses to OPTIONS requests for `/api/v1/users/me` and `/api/v1/users/logout` endpoints.

**High-Confidence Root Causes:**
- **Hardcoded localhost URLs in frontend bundles**: Built assets contain `http://localhost:8001/api/v1`, creating cross-origin requests from production domain
- **Missing production origin in CORS allowlist**: FastAPI CORS middleware only permits localhost origins, rejecting `http://5.223.41.154`

**Medium-Confidence Causes:**
- **Build environment misconfiguration**: `VITE_API_BASE_URL` not set during production build, causing fallback to hardcoded values

**Low-Confidence Causes:**
- **Nginx OPTIONS handling**: Proxy configuration appears correct; unlikely to be swallowing OPTIONS requests

The issue requires coordinated fixes across frontend build process, backend CORS configuration, and deployment procedures.

## 2. Evidence

### Browser/DevTools Observations
- **Error Pattern**: "Access to XMLHttpRequest at 'http://localhost:8001/api/v1/users/me' from origin 'http://5.223.41.154' has been blocked by CORS policy"
- **Request Headers**: `Origin: http://5.223.41.154`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: Authorization, Content-Type`
- **Response Status**: `400 Bad Request`
- **Response Message**: `Disallowed CORS origin`

### Curl Test Results
```bash
# Production domain OPTIONS (FAILS)
$ curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET'

HTTP/1.1 400 Bad Request
Server: nginx/1.18.0 (Ubuntu)
Content-Type: text/plain; charset=utf-8
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: Authorization, Content-Type
access-control-allow-credentials: true
Disallowed CORS origin

# Localhost OPTIONS (SUCCEEDS)
$ curl -i -X OPTIONS 'http://localhost:8001/api/v1/users/me' \
  -H 'Origin: http://localhost:5173'

HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:5173
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: Authorization, Content-Type
access-control-allow-credentials: true
OK
```

### Frontend Bundle Analysis
```bash
$ grep -r "http://localhost:8001" app/frontend/panel/dist/
app/frontend/panel/dist/assets/Parts--SJYm0y_.js:http://localhost:8001/api/v1
app/frontend/panel/dist/assets/Dashboard-BtsGDaNr.js:http://localhost:8001/api/v1
app/frontend/panel/dist/assets/Vehicles-lpVGk_vf.js:http://localhost:8001/api/v1
app/frontend/panel/dist/assets/Leads-DFXgfLO5.js:http://localhost:8001/api/v1
app/frontend/panel/dist/assets/Categories-BusJ4NDL.js:http://localhost:8001/api/v1
```

### Backend CORS Configuration
**File**: `app/api/main.py:47-54`
```python
cors_origins = [
    "http://localhost:5173",  # Admin panel
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Web portal
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# ❌ Production origin "http://5.223.41.154" is MISSING
```

### Nginx Configuration
**Proxy behavior confirmed working**: API calls to `/api/v1/users/login` succeed with 200 OK, indicating nginx correctly forwards requests to backend.

### Backend Logs
```
INFO: 127.0.0.1:55651 - "OPTIONS /api/v1/users/me HTTP/1.1" 400 Bad Request
INFO: 127.0.0.1:55657 - "OPTIONS /api/v1/users/logout HTTP/1.1" 400 Bad Request
```

## 3. Root Cause Analysis

### Primary Issue: Cross-Origin Architecture
The fundamental problem is an **unintentional cross-origin deployment**:

1. **Frontend Origin**: `http://5.223.41.154` (production server)
2. **API Target**: `http://localhost:8001` (hardcoded in bundles)

This creates cross-domain requests that trigger CORS preflight (OPTIONS) before actual API calls.

### Why Preflight Fails
1. **Browser sends OPTIONS** to `http://localhost:8001/api/v1/users/me` with `Origin: http://5.223.41.154`
2. **Backend receives OPTIONS** but rejects due to origin not in `cors_origins` allowlist
3. **Browser blocks subsequent requests** due to failed preflight

### Why Login POST Initially Succeeds
Simple POST requests to `/api/v1/users/login` bypass preflight in some cases but subsequent GET requests to `/api/v1/users/me` require preflight due to `Authorization` header.

### Nginx Role
Nginx acts as transparent proxy - it forwards requests but doesn't modify CORS behavior. The 400 responses originate from FastAPI, not nginx.

## 4. Structural Fixes (Prioritized)

### Priority 1: Same-Origin Deployment (RECOMMENDED)
**Objective**: Eliminate CORS entirely by serving API and frontend from same origin.

**Changes Required**:
- **Frontend**: Build with `VITE_API_BASE_URL=/api/v1` (relative path)
- **Nginx**: Proxy `/api/v1/*` to backend while serving frontend from document root
- **Result**: All requests become same-origin (`http://5.223.41.154` → `http://5.223.41.154/api/v1`)

**Benefits**:
- No CORS preflight required
- Simplified security model
- No hardcoded URLs in bundles

### Priority 2: Frontend Build Hygiene
**Objective**: Ensure production builds use relative API paths.

**Implementation**:
```bash
# Production build command
cd app/frontend/panel
VITE_API_BASE_URL='/api/v1' npm run build

# Verification
grep -r "localhost:8001" dist/ 
# Expected: No matches found
```

**File Changes**:
- `app/frontend/panel/package.json`: Add `"build:production"` script
- Build process: Set environment variables before build
- CI/CD: Add grep validation step

### Priority 3: Backend CORS Configuration (Fallback)
**Objective**: If cross-origin deployment is required, properly configure CORS.

**Changes Required**:
```python
# app/api/main.py
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174", 
    "http://127.0.0.1:5174",
    "http://5.223.41.154",     # ADD: Production HTTP
    "https://5.223.41.154",    # ADD: Production HTTPS
    # Consider: "*" for development only
]
```

**Verification**:
```bash
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'
# Expected: 200 OK with access-control-allow-origin header
```

### Priority 4: Nginx OPTIONS Handling (Defense in Depth)
**Objective**: Ensure OPTIONS requests reach backend or are handled gracefully.

**Current Config Analysis**: 
- Nginx appears to proxy OPTIONS correctly
- No evidence of request interception

**Fallback Option** (if backend unavailable):
```nginx
location /api/v1/ {
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Max-Age' 600 always;
        return 204;
    }
    proxy_pass http://127.0.0.1:8001/api/v1/;
    # ... existing proxy settings
}
```

### Priority 5: CI/CD Guardrails
**Objective**: Prevent regression through automated validation.

**Build Checks**:
```bash
# In CI pipeline after frontend build
echo "Checking for hardcoded localhost URLs..."
if grep -r "localhost:8001" app/frontend/panel/dist/; then
    echo "❌ Found hardcoded localhost URLs in production build"
    exit 1
fi

echo "Testing CORS preflight..."
curl -f -X OPTIONS "$PRODUCTION_URL/api/v1/users/me" \
  -H "Origin: $PRODUCTION_URL" \
  -H "Access-Control-Request-Method: GET"
```

**Deployment Smoke Tests**:
```bash
# Post-deployment validation
curl -f "$PRODUCTION_URL/panel/vite.svg"  # Asset serving
curl -f -X POST "$PRODUCTION_URL/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $PRODUCTION_URL" \
  -d '{"username_or_email":"admin","password":"test"}'
```

## 5. Verification / Reproduction Steps

### Pre-Fix Testing
```bash
# Confirm issue exists
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization'
# Expected: 400 Bad Request, "Disallowed CORS origin"

# Check bundle contamination
grep -r "http://localhost:8001" app/frontend/panel/dist/
# Expected: Multiple matches in JS files
```

### Post-Fix Testing
```bash
# Test same-origin deployment
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization'
# Expected: 200 OK with access-control-allow-origin: http://5.223.41.154

# Verify clean bundles
grep -r "localhost:8001" app/frontend/panel/dist/
# Expected: No matches found

# Test asset serving
curl -I http://5.223.41.154/panel/vite.svg
# Expected: 200 OK

# End-to-end authentication test
curl -i -X POST 'http://5.223.41.154/api/v1/users/login' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://5.223.41.154' \
  -d '{"username_or_email":"admin","password":"rgY3q@7RV6d*"}'
# Expected: 200 OK with JWT token

TOKEN="<extract_from_above>"
curl -i -X GET 'http://5.223.41.154/api/v1/users/me' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Origin: http://5.223.41.154'
# Expected: 200 OK with user data
```

### Backend Direct Testing
```bash
# Test backend CORS directly (bypassing nginx)
curl -i -X OPTIONS 'http://127.0.0.1:8001/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'
# Expected: 200 OK (after backend CORS fix)
```

## 6. Acceptance Criteria

### Functional Requirements
- [ ] **No browser CORS errors**: DevTools console shows no "blocked by CORS policy" messages
- [ ] **OPTIONS requests succeed**: All preflight requests return 200/204 with proper headers
- [ ] **Authentication flow works**: Login → /users/me → logout completes without errors
- [ ] **Asset serving functional**: Static files under `/panel/` load correctly

### Technical Requirements
- [ ] **Clean bundles**: `grep -r "localhost:8001" dist/` returns no matches
- [ ] **Proper CORS headers**: `access-control-allow-origin` matches request origin
- [ ] **Relative API URLs**: All frontend API calls use `/api/v1` base path
- [ ] **Nginx proxy functional**: `/api/v1/*` requests route to backend correctly

### Quality Gates
- [ ] **CI smoke tests pass**: Automated preflight and asset tests succeed
- [ ] **Build validation**: Production build process includes URL validation
- [ ] **Monitoring ready**: CORS error tracking in place (optional)

### Performance Requirements
- [ ] **No degradation**: Authentication latency unchanged
- [ ] **Cache headers**: Static assets have appropriate cache headers

## 7. Residual Recommendations

### Development Process
1. **Lint Rule**: Add ESLint rule to forbid absolute API URLs in frontend code
   ```javascript
   // .eslintrc.js
   rules: {
     'no-absolute-api-urls': 'error'
   }
   ```

2. **Environment Management**: Centralize API base URL configuration
   ```javascript
   // config/api.js - single source of truth
   export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
   ```

### Documentation
3. **CORS Policy Documentation**: Create `/docs/ops/cors-policy.md` documenting:
   - Allowed origins for each environment
   - Required headers and methods
   - Troubleshooting guide

4. **Deployment Checklist**: Update deployment docs with CORS verification steps

### Monitoring
5. **Observability**: Add metrics for:
   - OPTIONS request 4xx count by endpoint
   - CORS rejection rate by origin
   - Authentication flow success rate

6. **Alerting**: Configure alerts for:
   - Spike in CORS 4xx responses
   - Asset 404s under `/panel/`

### Future Architecture
7. **Domain-Based Deployment**: Plan migration from IP-based to domain-based deployment
   - Benefits: Proper SSL certificates, cleaner CORS policy
   - Timeline: Consider for next major release

8. **API Gateway**: Evaluate API gateway for centralized CORS/security handling
   - Candidates: Nginx Plus, Kong, AWS API Gateway
   - Benefits: Unified policy management

## 8. Appendices

### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name 5.223.41.154;
    
    # Frontend assets
    location / {
        root /var/www/html/web;
        try_files $uri $uri/ /index.html;
    }
    
    # Admin panel
    location /panel/ {
        alias /var/www/html/panel/;
        try_files $uri $uri/ /panel/index.html;
    }
    
    # API proxy
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if backend doesn't handle)
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }
}
```

### Example FastAPI CORS Configuration
```python
# app/api/main.py
from fastapi.middleware.cors import CORSMiddleware

# Production-ready CORS configuration
cors_origins = [
    # Development
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    # Production
    "http://5.223.41.154",
    "https://5.223.41.154",
    # Future: add domain when available
    # "https://admin.yourapp.com",
    # "https://yourapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # Or specific: ["Authorization", "Content-Type"]
    max_age=600,  # Cache preflight for 10 minutes
)
```

### Example Build Script
```json
{
  "scripts": {
    "build": "vite build",
    "build:production": "VITE_API_BASE_URL=/api/v1 vite build && npm run verify:build",
    "verify:build": "scripts/verify-build.sh"
  }
}
```

```bash
#!/bin/bash
# scripts/verify-build.sh
echo "🔍 Verifying production build..."

if grep -r "localhost:8001" dist/; then
    echo "❌ Found hardcoded localhost URLs"
    exit 1
fi

if grep -r "127.0.0.1:8001" dist/; then
    echo "❌ Found hardcoded 127.0.0.1 URLs"
    exit 1
fi

echo "✅ Build verification passed"
```

### Example Curl Test Suite
```bash
#!/bin/bash
# test-cors.sh
HOST="http://5.223.41.154"

echo "Testing CORS preflight..."
curl -i -X OPTIONS "$HOST/api/v1/users/me" \
  -H "Origin: $HOST" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"

echo -e "\nTesting asset serving..."
curl -I "$HOST/panel/vite.svg"

echo -e "\nTesting login flow..."
curl -i -X POST "$HOST/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $HOST" \
  -d '{"username_or_email":"admin","password":"test"}'
```

---

## Top-3 Priority Actions

1. **Frontend Team**: Rebuild admin panel with `VITE_API_BASE_URL=/api/v1` and verify no hardcoded URLs in dist/ (15 minutes)

2. **Backend Team**: Add production origin `"http://5.223.41.154"` to CORS origins in `app/api/main.py` (5 minutes)

3. **DevOps Team**: Deploy updated frontend assets and restart backend service, then run verification tests (10 minutes)

**Total estimated resolution time**: 30 minutes
