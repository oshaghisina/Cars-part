# CORS Preflight Diagnostic Report

## 1. Executive Summary

The production admin panel at `http://5.223.41.154/panel/` is experiencing **CORS preflight failures** that prevent proper authentication. The root cause is a **hardcoded API base URL** (`http://localhost:8001/api/v1`) in the built frontend assets, causing cross-origin requests from the production domain to be blocked by the browser's CORS policy.

**Primary Issue**: The frontend was built with `localhost:8001` hardcoded in the JavaScript bundles, making requests from `http://5.223.41.154` to `http://localhost:8001` cross-origin, which triggers CORS preflight requests that fail due to the production server's CORS configuration not allowing the production domain.

**Confidence Levels**:
- **High**: Hardcoded localhost URLs in built assets (confirmed via grep)
- **High**: CORS origin restriction (confirmed via curl tests)
- **Medium**: Missing production environment variable during build
- **Low**: Nginx configuration issues (nginx is properly proxying)

## 2. Evidence Inventory

### Runtime Observations
- **Failing Request URLs**: `http://localhost:8001/api/v1/users/me`, `http://localhost:8001/api/v1/users/logout`
- **Origins**: `http://5.223.41.154` (production domain)
- **Request Headers**: `Origin: http://5.223.41.154`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: Authorization, Content-Type`
- **Response Status**: `400 Bad Request`
- **Response Headers**: `access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH`, `access-control-allow-headers: Authorization, Content-Type`, `access-control-allow-credentials: true`
- **Error Message**: `Disallowed CORS origin`

### Backend Evidence
```bash
# OPTIONS request from production domain (FAILS)
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'

# Response: 400 Bad Request with "Disallowed CORS origin"

# OPTIONS request from localhost:5173 (SUCCEEDS)
curl -i -X OPTIONS 'http://localhost:8001/api/v1/users/me' \
  -H 'Origin: http://localhost:5173' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'

# Response: 200 OK with proper CORS headers

# Direct API call (SUCCEEDS)
curl -i -X POST 'http://5.223.41.154/api/v1/users/login' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://5.223.41.154' \
  -d '{"username_or_email": "admin", "password": "rgY3q@7RV6d*"}'

# Response: 200 OK with JWT token
```

### Backend Logs
From terminal output, observed:
- `INFO: 127.0.0.1:55651 - "OPTIONS /api/v1/users/me HTTP/1.1" 400 Bad Request`
- `INFO: 127.0.0.1:55657 - "OPTIONS /api/v1/users/logout HTTP/1.1" 400 Bad Request`

### Local vs Production Difference
- **Local**: Requests from `localhost:5173` to `localhost:8001` succeed (same-origin)
- **Production**: Requests from `5.223.41.154` to `localhost:8001` fail (cross-origin)

## 3. Code/Config Surface Scan

### Search Results

#### Absolute API URLs in Frontend
```bash
# Found hardcoded localhost URLs in built assets
grep -r "http://localhost:8001" app/frontend/panel/dist/
# Result: Found in multiple JS bundles
```

**Files with hardcoded URLs**:
- `app/frontend/panel/dist/assets/Parts--SJYm0y_.js`
- `app/frontend/panel/dist/assets/Dashboard-BtsGDaNr.js`
- `app/frontend/panel/dist/assets/Vehicles-lpVGk_vf.js`
- `app/frontend/panel/dist/assets/Leads-DFXgfLO5.js`
- `app/frontend/panel/dist/assets/Categories-BusJ4NDL.js`

**Source**: `app/frontend/web/src/api/pdp.js:6`
```javascript
const API_BASE_URL = 'http://localhost:8001/api/v1'
```

#### Vite Configuration
**File**: `app/frontend/panel/vite.config.js`
```javascript
export default defineConfig({
  base: process.env.VITE_BASE || '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

#### API Base URL Configuration
**File**: `app/frontend/panel/src/api/baseUrl.js`
```javascript
export const resolveApiBaseUrl = () => {
  const envValue = import.meta?.env?.VITE_API_BASE_URL;
  if (envValue && envValue.trim()) {
    return stripTrailingSlash(envValue.trim());
  }
  // Falls back to window.location.origin + /api/v1
  return stripTrailingSlash(`${window.location.origin}${DEFAULT_API_PATH}`);
};
```

#### FastAPI CORS Configuration
**File**: `app/api/main.py:47-61`
```python
cors_origins = [
    "http://localhost:5173",  # Admin panel
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Web portal
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
```

**Critical Finding**: Production domain `http://5.223.41.154` is **NOT** in the `cors_origins` list.

## 4. Reproduction Checklist

### Commands to Run (in order)

#### Test 1: Local CORS Preflight (should succeed)
```bash
curl -i -X OPTIONS 'http://localhost:8001/api/v1/users/me' \
  -H 'Origin: http://localhost:5173' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'
```
**Expected**: 200 OK with `access-control-allow-origin: http://localhost:5173`

#### Test 2: Production CORS Preflight (currently fails)
```bash
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'
```
**Expected**: 400 Bad Request with "Disallowed CORS origin"

#### Test 3: Direct API Call (should succeed)
```bash
curl -i -X POST 'http://5.223.41.154/api/v1/users/login' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://5.223.41.154' \
  -d '{"username_or_email": "admin", "password": "rgY3q@7RV6d*"}'
```
**Expected**: 200 OK with JWT token

#### Test 4: Asset Base Check
```bash
curl -I http://5.223.41.154/panel/vite.svg
```
**Expected**: 200 OK (if assets are properly deployed)

### Remote vs Local Testing
- **Remote machine**: Use production domain in Origin header
- **Local server**: Test without Origin header to confirm backend works
- **Browser simulation**: Use curl with exact headers from browser dev tools

## 5. Likely Root Causes (ranked)

### 1. **Hardcoded localhost URLs in built frontend** (HIGH confidence)
- **Explanation**: Frontend was built with `localhost:8001` hardcoded, causing cross-origin requests
- **Evidence**: Grep results show `http://localhost:8001/api/v1` in built JS files
- **Impact**: Browser blocks requests due to CORS policy

### 2. **Missing production domain in CORS origins** (HIGH confidence)
- **Explanation**: FastAPI CORS middleware doesn't allow `http://5.223.41.154` origin
- **Evidence**: `cors_origins` list only contains localhost domains
- **Impact**: Even if frontend used relative URLs, CORS would still fail

### 3. **Missing VITE_API_BASE_URL during build** (MEDIUM confidence)
- **Explanation**: Frontend build didn't use production API base URL
- **Evidence**: `VITE_API_BASE_URL` environment variable not set during build
- **Impact**: Frontend falls back to hardcoded localhost URLs

### 4. **Nginx configuration issues** (LOW confidence)
- **Explanation**: Nginx might not be properly proxying OPTIONS requests
- **Evidence**: Nginx is responding with backend CORS headers, suggesting proper proxying
- **Impact**: Minimal - nginx appears to be working correctly

## 6. Non-invasive Diagnostic Steps

### Confirm Hardcoded URLs
```bash
# Check built assets for hardcoded URLs
grep -r "http://localhost:8001" app/frontend/panel/dist/
grep -r "http://5\.223\.41\.154" app/frontend/panel/dist/
```

### Test CORS Configuration
```bash
# Test with production domain in CORS origins (temporary)
# Edit app/api/main.py to add "http://5.223.41.154" to cors_origins
# Restart backend and test OPTIONS request
```

### Verify Environment Variables
```bash
# Check what environment variables were used during build
echo "VITE_API_BASE_URL: $VITE_API_BASE_URL"
echo "VITE_BASE: $VITE_BASE"
```

### Test Asset Serving
```bash
# Verify assets are served correctly
curl -I http://5.223.41.154/panel/
curl -I http://5.223.41.154/panel/vite.svg
```

## 7. Structural Fixes (prioritized)

### 1. **Add production domain to CORS origins** (IMMEDIATE)
- **File**: `app/api/main.py`
- **Change**: Add `"http://5.223.41.154"` to `cors_origins` list
- **Verification**: Test OPTIONS request returns 200 OK
- **Rollback**: Remove domain from list

### 2. **Rebuild frontend with correct API base URL** (IMMEDIATE)
- **Command**: `VITE_API_BASE_URL='/api/v1' npm run build`
- **Deploy**: Copy built assets to nginx directory
- **Verification**: Check built assets for relative URLs only
- **Rollback**: Rebuild with previous settings

### 3. **Centralize API client configuration** (MEDIUM)
- **File**: `app/frontend/panel/src/api/baseUrl.js`
- **Change**: Ensure all stores use centralized API base URL
- **Verification**: No hardcoded URLs in source code
- **Rollback**: Revert to individual store configurations

### 4. **Add production build script** (MEDIUM)
- **File**: `app/frontend/panel/package.json`
- **Change**: Add `"build:production": "VITE_API_BASE_URL='/api/v1' vite build"`
- **Verification**: Script produces correct build
- **Rollback**: Remove script

### 5. **Add CI preflight tests** (LOW)
- **File**: `.github/workflows/`
- **Change**: Add OPTIONS request tests to CI
- **Verification**: Tests pass in CI
- **Rollback**: Remove test step

## 8. Quick Mitigation (temporary)

### Mitigation 1: Add production domain to CORS (5 minutes)
```python
# In app/api/main.py, add to cors_origins:
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://5.223.41.154",  # ADD THIS LINE
]
```
**Revert**: Remove the added line

### Mitigation 2: Rebuild frontend with correct API base (10 minutes)
```bash
cd app/frontend/panel
VITE_API_BASE_URL='/api/v1' npm run build
# Deploy built assets to production
```
**Revert**: Rebuild with `VITE_API_BASE_URL='http://localhost:8001/api/v1'`

### Mitigation 3: Nginx OPTIONS handler (15 minutes)
```nginx
# Add to nginx config
location /api/ {
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Max-Age' 600 always;
        return 204;
    }
    proxy_pass http://127.0.0.1:8001/api/;
    # ... other proxy settings
}
```
**Revert**: Remove the OPTIONS handler

## 9. CI/CD & Testing Recommendations

### Automated Tests to Add
```bash
# Preflight test
curl -f -X OPTIONS "$API_BASE_URL/users/me" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"

# Asset availability test
curl -f "$FRONTEND_URL/panel/vite.svg"

# Login smoke test
curl -f -X POST "$API_BASE_URL/users/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $FRONTEND_URL" \
  -d '{"username_or_email": "admin", "password": "test"}'
```

### Monitoring Metrics
- **CORS preflight 4xx count** per route
- **401/403 spikes** in authentication endpoints
- **Asset 404s** for `/panel/*` paths
- **API response times** for OPTIONS requests

## 10. Acceptance Criteria & Rollout Checklist

### Pass/Fail Criteria
- [ ] Browser no longer reports CORS errors for `/api/v1/users/me` and `/api/v1/users/logout`
- [ ] OPTIONS preflight returns 200/204 with `Access-Control-Allow-Origin: http://5.223.41.154`
- [ ] Login endpoint returns 200 with JWT token for admin credentials
- [ ] Asset `/panel/vite.svg` served under `/panel/` (HTTP 200)
- [ ] No hardcoded `localhost:8001` URLs in built frontend assets

### Rollout Steps
1. **Backend**: Add production domain to CORS origins
2. **Backend**: Restart API service
3. **Frontend**: Rebuild with `VITE_API_BASE_URL='/api/v1'`
4. **Frontend**: Deploy built assets to nginx
5. **Test**: Run acceptance criteria tests
6. **Monitor**: Check logs for CORS errors

## 11. Residual Architectural Recommendations

### Strategic Improvements
- **Enforce same-origin deployment** for SPAs + API to eliminate CORS complexity
- **Add "no absolute API URLs" lint rule** in frontend CI
- **Centralize API client** and environment flags in single configuration
- **Add pre-deploy CI preflight tests** to catch CORS issues early
- **Document canonical CORS policy** in repository documentation

### Long-term Architecture
- Consider using **subdomain-based routing** (api.domain.com, panel.domain.com)
- Implement **API gateway** for centralized CORS handling
- Use **environment-specific build configurations** instead of runtime detection

## 12. Appendices

### Grep Commands Used
```bash
# Search for hardcoded URLs
grep -r "http://localhost:8001\|http://127.0.0.1:8001\|http://5\.\|http[s]?://" app/frontend/

# Search for API base configurations
grep -r "API_BASE\|api/v1\|localhost:8001" app/frontend/

# Search for CORS configuration
grep -r "CORSMiddleware\|allow_origins\|allow_headers\|allow_methods" app/
```

### Files Inspected
- `app/api/main.py` (CORS configuration)
- `app/frontend/panel/src/api/baseUrl.js` (API base URL resolution)
- `app/frontend/panel/src/api/client.js` (API client configuration)
- `app/frontend/panel/vite.config.js` (Vite configuration)
- `app/frontend/panel/package.json` (Build scripts)
- `app/frontend/panel/dist/assets/*.js` (Built frontend assets)

### Raw Curl Outputs
```bash
# Production OPTIONS (FAILS)
HTTP/1.1 400 Bad Request
Server: nginx/1.18.0 (Ubuntu)
Content-Type: text/plain; charset=utf-8
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: Authorization, Content-Type
access-control-allow-credentials: true
Disallowed CORS origin

# Local OPTIONS (SUCCEEDS)
HTTP/1.1 200 OK
Server: uvicorn
access-control-allow-origin: http://localhost:5173
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: Authorization, Content-Type
access-control-allow-credentials: true
OK
```

### Suggested Configurations

#### FastAPI CORS Middleware
```python
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://5.223.41.154",  # Production domain
    "https://5.223.41.154", # HTTPS variant
]
```

#### Nginx Configuration
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## Priority Action Items

1. **Backend Team**: Add `"http://5.223.41.154"` to CORS origins in `app/api/main.py` (5 minutes)
2. **Frontend Team**: Rebuild admin panel with `VITE_API_BASE_URL='/api/v1'` (10 minutes)  
3. **DevOps Team**: Deploy updated frontend assets to nginx directory (5 minutes)

**Total estimated time to resolution**: 20 minutes
