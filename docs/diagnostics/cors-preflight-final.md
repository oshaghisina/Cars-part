# CORS Preflight Issue - Final Resolution Report

## 1. Executive Summary

The production admin panel at `http://5.223.41.154/panel/` experiences systematic CORS preflight failures preventing user authentication. Browser traces show the frontend making cross-origin requests to `http://localhost:8001/api/v1/users/me` and `/api/v1/users/logout` from the production origin, resulting in 400 Bad Request responses with "Disallowed CORS origin" errors.

**Converging Evidence from All Analysis**:
All three diagnostic documents confirm the same core issue: production authentication fails due to CORS preflight rejections on OPTIONS requests. The problem manifests immediately after login when the frontend attempts to validate the user session.

**High-Confidence Root Causes**:
1. **Production origin missing in FastAPI CORSMiddleware `allow_origins`**: The backend only whitelists localhost origins, rejecting requests from `http://5.223.41.154`
2. **Frontend bundle hardcodes `http://localhost:8001/api/v1`**: Built assets contain absolute localhost URLs, forcing cross-origin requests from production domain

**Medium-Confidence Causes**:
- **Build environment misconfiguration**: `VITE_API_BASE_URL` not set during production build, causing fallback to hardcoded values
- **Stale deployment**: Possibility that updated builds weren't properly deployed to production

**Low-Confidence Causes**:
- **Nginx OPTIONS handling**: Proxy configuration appears correct; nginx transparently forwards OPTIONS to backend

## 2. Evidence (Merged)

### DevTools/Browser Errors
- **Error Pattern**: "Access to XMLHttpRequest at 'http://localhost:8001/api/v1/users/me' from origin 'http://5.223.41.154' has been blocked by CORS policy"
- **Failed Endpoints**: `/api/v1/users/me`, `/api/v1/users/logout`
- **Request Headers**: `Origin: http://5.223.41.154`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: Authorization, Content-Type`
- **Response Status**: `400 Bad Request`
- **Response Message**: `Disallowed CORS origin`

### Curl OPTIONS Tests
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

**Source File Evidence**:
- `app/frontend/panel/src/views/Parts.vue:412`: `const API_BASE = "http://localhost:8001/api/v1";`
- `app/frontend/web/src/api/pdp.js:6`: `const API_BASE_URL = 'http://localhost:8001/api/v1'`

### FastAPI CORS Configuration
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

### Nginx Configuration Verification
Nginx correctly proxies `/api/v1/` requests to backend without modification. The 400 CORS responses originate from FastAPI, not nginx, confirming the proxy is working as expected.

### Backend Logs
```
INFO: 127.0.0.1:55651 - "OPTIONS /api/v1/users/me HTTP/1.1" 400 Bad Request
INFO: 127.0.0.1:55657 - "OPTIONS /api/v1/users/logout HTTP/1.1" 400 Bad Request
```

## 3. Root Cause Analysis

### Primary Issue: Unintentional Cross-Origin Architecture
The production deployment creates an unintended cross-origin setup:
- **Frontend Origin**: `http://5.223.41.154` (production server)
- **API Target**: `http://localhost:8001` (hardcoded in bundles)

This triggers CORS preflight (OPTIONS) for requests with custom headers like `Authorization`.

### Why Preflight Fails
1. Browser sends OPTIONS to `http://localhost:8001/api/v1/users/me` with `Origin: http://5.223.41.154`
2. Backend receives OPTIONS but rejects due to origin not in `cors_origins` allowlist
3. Browser blocks subsequent requests due to failed preflight

### Why Some Requests Initially Succeed
Simple POST requests (like login) may bypass preflight in certain cases, but subsequent GET requests with `Authorization` headers always require preflight.

### Nginx Role (Diagnostic)
**Direct backend test**:
```bash
# Test backend directly (bypasses nginx)
curl -i -X OPTIONS 'http://127.0.0.1:8001/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'
# Expected: Same 400 Bad Request, confirming nginx is not the cause
```

**Via nginx test**:
```bash
# Test via nginx proxy
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'
# Result: Identical 400 response, proving nginx transparently forwards
```

## 4. Structural Fixes (Final)

### Frontend Fixes
**Enforce Relative Base URL**:
- **Target**: All store files and API clients must use `/api/v1` instead of absolute URLs
- **Build Command**: `VITE_API_BASE_URL='/api/v1' npm run build`
- **Verification**: `grep -r "localhost:8001" dist/` must return no matches
- **Files to Update**: 
  - `app/frontend/panel/src/views/Parts.vue:412`
  - `app/frontend/web/src/api/pdp.js:6`
  - All store files in `app/frontend/panel/src/stores/`

**CI Build Step**:
```bash
# Add to CI pipeline
echo "Checking for hardcoded localhost URLs..."
if grep -r "localhost:8001" app/frontend/panel/dist/; then
    echo "❌ Found hardcoded localhost URLs in production build"
    exit 1
fi
```

### Backend (FastAPI) Fixes
**Add Production Origins**:
```python
# app/api/main.py
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # ADD PRODUCTION ORIGINS
    "http://5.223.41.154",     # Production HTTP
    "https://5.223.41.154",    # Production HTTPS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Ensure all methods allowed
    allow_headers=["*"],  # Ensure all headers allowed
    max_age=600,
)
```

### Nginx Configuration
**Current proxy works correctly**; no changes needed. Optional defense-in-depth OPTIONS handler:
```nginx
location /api/v1/ {
    # Optional: Handle OPTIONS directly
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Max-Age' 600 always;
        return 204;
    }
    
    proxy_pass http://127.0.0.1:8001/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### CI/CD Integration
**Smoke Tests**:
```bash
#!/bin/bash
# Post-deployment verification

# Test CORS preflight
echo "Testing CORS preflight..."
curl -f -X OPTIONS "$PRODUCTION_URL/api/v1/users/me" \
  -H "Origin: $PRODUCTION_URL" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"

# Test asset serving  
echo "Testing asset serving..."
curl -f "$PRODUCTION_URL/panel/vite.svg"

# Test login flow
echo "Testing login flow..."
curl -f -X POST "$PRODUCTION_URL/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $PRODUCTION_URL" \
  -d '{"username_or_email":"admin","password":"test"}'
```

## 5. Verification Plan

### Pre-Fix Testing
```bash
# Confirm issue exists
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET'
# Expected: 400 Bad Request, "Disallowed CORS origin"

# Check bundle contamination
grep -r "http://localhost:8001" app/frontend/panel/dist/
# Expected: Multiple matches
```

### Post-Fix Testing
```bash
# Test OPTIONS success
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization'
# Expected: 200 OK with access-control-allow-origin: http://5.223.41.154

# Verify clean bundles
grep -r "localhost:8001" app/frontend/panel/dist/
# Expected: No matches

# Test asset serving
curl -I http://5.223.41.154/panel/vite.svg
# Expected: 200 OK

# End-to-end authentication
TOKEN=$(curl -s -X POST 'http://5.223.41.154/api/v1/users/login' \
  -H 'Content-Type: application/json' \
  -d '{"username_or_email":"admin","password":"rgY3q@7RV6d*"}' | jq -r .access_token)

curl -i -X GET 'http://5.223.41.154/api/v1/users/me' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Origin: http://5.223.41.154'
# Expected: 200 OK with user data
```

### Backend Direct vs Nginx Comparison
```bash
# Direct to backend
curl -i -X OPTIONS 'http://127.0.0.1:8001/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'

# Via nginx proxy  
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154'

# Compare responses - should be identical after backend fix
```

## 6. Acceptance Criteria

### Functional Requirements
- [ ] **No browser CORS errors**: DevTools console shows no "blocked by CORS policy" messages
- [ ] **OPTIONS requests succeed**: All preflight requests return 200/204 with proper `Access-Control-Allow-Origin` headers
- [ ] **Authentication flow works**: Login → /users/me → logout completes without errors
- [ ] **Asset serving functional**: Static files under `/panel/` load correctly (test with vite.svg)

### Technical Requirements
- [ ] **Clean bundles**: `grep -r "localhost:8001" dist/` returns no matches after build
- [ ] **Proper CORS headers**: Response includes `access-control-allow-origin` matching request origin
- [ ] **Relative API URLs**: All frontend API calls use `/api/v1` base path
- [ ] **Backend accepts production origin**: FastAPI CORS middleware includes production domain

### Quality Gates
- [ ] **CI smoke tests pass**: Automated preflight and authentication tests succeed
- [ ] **Build validation**: Production build process validates no hardcoded URLs
- [ ] **No performance degradation**: Authentication latency unchanged

## 7. Residual Recommendations

### Development Process
1. **Lint Rule**: Add ESLint rule to forbid absolute API URLs in frontend code
   ```javascript
   // .eslintrc.js - prevent absolute API URLs
   rules: {
     'no-absolute-api-urls': ['error', {
       message: 'Use relative API paths (/api/v1) instead of absolute URLs'
     }]
   }
   ```

2. **Environment Management**: Centralize API base URL configuration
   ```javascript
   // Single source of truth for API base URL
   export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
   ```

### Documentation
3. **CORS Policy Documentation**: Create `/docs/ops/cors-policy.md`:
   - Allowed origins for each environment
   - Required headers and methods
   - Troubleshooting guide for CORS issues

4. **Build Process Documentation**: Update deployment guides with:
   - Required environment variables for production builds
   - Bundle verification steps
   - CORS testing procedures

### Monitoring
5. **Observability**: Add metrics for:
   - OPTIONS request 4xx count by endpoint
   - CORS rejection rate by origin
   - Authentication flow success rate
   - Asset serving 404 rates

6. **Alerting**: Configure alerts for:
   - Spike in CORS 4xx responses
   - Asset 404s under `/panel/`
   - Authentication failure rate increases

## 8. Appendices

### Example FastAPI CORS Configuration
```python
# app/api/main.py - Complete CORS configuration
from fastapi.middleware.cors import CORSMiddleware

cors_origins = [
    # Development
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174", 
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Production
    "http://5.223.41.154",
    "https://5.223.41.154",
    # Future domain-based deployment
    # "https://admin.yourapp.com",
    # "https://yourapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

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
    
    # API proxy (current working configuration)
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Example Curl Test Commands
```bash
#!/bin/bash
# cors-test-suite.sh
HOST="http://5.223.41.154"

echo "=== CORS Preflight Test ==="
curl -i -X OPTIONS "$HOST/api/v1/users/me" \
  -H "Origin: $HOST" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"

echo -e "\n=== Asset Serving Test ==="
curl -I "$HOST/panel/vite.svg"

echo -e "\n=== Login Flow Test ==="
curl -i -X POST "$HOST/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $HOST" \
  -d '{"username_or_email":"admin","password":"test"}'

echo -e "\n=== Bundle Verification ==="
echo "Checking for hardcoded URLs in deployed bundle:"
ssh root@5.223.41.154 "grep -r 'localhost:8001' /var/www/html/panel/ || echo 'No hardcoded URLs found'"
```

### Example CI Pipeline Snippet
```bash
#!/bin/bash
# ci-cors-validation.sh

set -e

echo "🔍 Validating frontend build for CORS compliance..."

# Check for hardcoded localhost URLs
if grep -r "localhost:8001" app/frontend/panel/dist/; then
    echo "❌ Found hardcoded localhost URLs in production build"
    exit 1
fi

if grep -r "127.0.0.1:8001" app/frontend/panel/dist/; then
    echo "❌ Found hardcoded 127.0.0.1 URLs in production build" 
    exit 1
fi

echo "✅ Frontend build validation passed"

# Test CORS if deployment target is available
if [ -n "$DEPLOYMENT_URL" ]; then
    echo "🌐 Testing CORS preflight on $DEPLOYMENT_URL..."
    
    curl -f -X OPTIONS "$DEPLOYMENT_URL/api/v1/users/me" \
      -H "Origin: $DEPLOYMENT_URL" \
      -H "Access-Control-Request-Method: GET" \
      -H "Access-Control-Request-Headers: Authorization" \
      || (echo "❌ CORS preflight test failed" && exit 1)
    
    echo "✅ CORS preflight test passed"
fi
```

---

## 📋 **Final To-Do List by Team**

### Frontend Team (15 minutes)
1. **Remove hardcoded URLs**: Update `app/frontend/panel/src/views/Parts.vue:412` and `app/frontend/web/src/api/pdp.js:6` to use relative `/api/v1` paths
2. **Rebuild with environment variable**: `cd app/frontend/panel && VITE_API_BASE_URL='/api/v1' npm run build`
3. **Verify clean build**: `grep -r "localhost:8001" dist/` should return no matches

### Backend Team (5 minutes)
1. **Add production origin**: Add `"http://5.223.41.154"` and `"https://5.223.41.154"` to `cors_origins` in `app/api/main.py`
2. **Restart backend service**: Deploy changes and restart API server
3. **Verify with curl**: Test OPTIONS request returns 200 OK with proper CORS headers

### DevOps Team (10 minutes)
1. **Deploy frontend**: Copy updated `dist/` to `/var/www/html/panel/` on production server
2. **Run verification tests**: Execute curl OPTIONS and asset serving tests
3. **Monitor logs**: Check for any CORS-related errors in nginx and application logs

**Total estimated resolution time**: 30 minutes
