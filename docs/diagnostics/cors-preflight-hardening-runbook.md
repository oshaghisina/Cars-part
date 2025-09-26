# CORS Preflight Hardening Runbook

## Executive Overview

**Where We Were**: Production admin panel at `http://5.223.41.154/panel/` experienced CORS preflight failures preventing user authentication. Browser DevTools showed "blocked by CORS policy" errors for `/api/v1/users/me` and `/api/v1/users/logout` endpoints.

**What's Fixed**: 
- **Production origin in CORS**: Added `"http://5.223.41.154"` to FastAPI `cors_origins` allowlist
- **Relative API paths**: Rebuilt frontend with `VITE_API_BASE_URL=/api/v1` for same-origin requests
- **Source cleanup**: Removed hardcoded `localhost:8001` URLs from frontend source files

**Why It Broke**: Frontend bundles contained hardcoded `http://localhost:8001/api/v1` URLs, forcing cross-origin requests from the production domain that were rejected by the backend CORS policy which only allowed localhost origins.

**Goal of This Package**: Provide teams with validated procedures, automated scripts, and reference configurations to maintain CORS stability and prevent regressions.

## Fast Path Implementation (30-45 minutes)

### Frontend Team (15 minutes)

#### ✅ **Step 1: Rebuild Admin Panel**
```bash
cd app/frontend/panel
VITE_API_BASE_URL='/api/v1' npm run build
```

#### ✅ **Step 2: Verify Clean Build**
```bash
# Check for hardcoded localhost URLs (should be empty)
grep -r '"http://localhost:8001' dist/ | grep -v '\.map'

# Verify relative paths are used (should show matches)
grep -r '/api/v1' dist/ | head -3
```

#### ✅ **Step 3: Deploy Static Assets**
```bash
# Method depends on your deployment process
# Example: Copy to nginx directory
cp -r dist/* /var/www/html/panel/
```

### Backend Team (10 minutes)

#### ✅ **Step 1: CORS Origins Configuration**
Ensure `app/api/main.py` contains production origins:
```python
cors_origins = [
    # Development
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
    # Production (required)
    "http://5.223.41.154",     # Production HTTP
    "https://5.223.41.154",    # Production HTTPS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Only if using cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],  # Minimum required
    max_age=600,
)
```

#### ✅ **Step 2: Service Restart** 
```bash
# Restart backend service
systemctl restart china-car-parts-api
# Or trigger blue-green deployment
```

### DevOps Team (10 minutes)

#### ✅ **Step 1: Nginx Proxy Verification**
```nginx
# Confirm nginx configuration (should already be working)
location /api/v1/ {
    proxy_pass http://127.0.0.1:8001/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

#### ✅ **Step 2: Reload & Validate**
```bash
nginx -t && nginx -s reload
./ops/scripts/smoke_cors.sh http://5.223.41.154
```

## Smoke Tests (Copy-Paste Ready)

### Manual Testing Commands

#### Test 1: Asset Serving
```bash
curl -I http://5.223.41.154/panel/vite.svg
# Expected: HTTP/1.1 200 OK
```

#### Test 2: CORS Preflight  
```bash
curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
  -H 'Origin: http://5.223.41.154' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'

# Expected Response:
# HTTP/1.1 200 OK
# access-control-allow-origin: http://5.223.41.154
# access-control-allow-headers: Authorization, Content-Type
```

#### Test 3: Login Flow
```bash
curl -i -X POST 'http://5.223.41.154/api/v1/users/login' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://5.223.41.154' \
  -d '{"username_or_email":"admin","password":"YOUR_PASSWORD"}'

# Expected: 200 OK with access_token
```

#### Test 4: Protected Endpoint
```bash
# Using token from login response:
curl -i -X GET 'http://5.223.41.154/api/v1/users/me' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H 'Origin: http://5.223.41.154'

# Expected: 200 OK with user data
```

### Automated Smoke Testing
```bash
# Quick validation
./ops/scripts/smoke_cors.sh http://5.223.41.154

# With authentication testing
HOST=http://5.223.41.154 USERNAME=admin PASSWORD=your_password \
  ./ops/scripts/smoke_cors.sh
```

## Acceptance Criteria

### Critical Requirements (Must Pass)
- [ ] **No CORS errors in browser**: DevTools console shows no "blocked by CORS policy" messages
- [ ] **OPTIONS returns 200/204**: Preflight requests succeed with `Access-Control-Allow-Origin` header matching request origin
- [ ] **Authorization header allowed**: CORS response includes `Authorization` in `Access-Control-Allow-Headers`
- [ ] **Login → /me flow works**: End-to-end authentication completes without CORS failures
- [ ] **Clean production bundles**: No hardcoded `localhost:8001` URLs in dist/ (excluding source maps)

### Important Requirements (Should Pass)
- [ ] **Asset serving functional**: `/panel/vite.svg` returns 200 OK
- [ ] **Backend logs clean**: No recent OPTIONS 400 errors in application logs
- [ ] **Performance maintained**: Authentication latency unchanged from baseline
- [ ] **Development still works**: Local development environment unaffected

### Optional Enhancements (Nice to Have)
- [ ] **CI integration**: Pipeline includes automated CORS validation
- [ ] **Monitoring configured**: Alerts set up for CORS 4xx spikes
- [ ] **Build validation**: Automated checks prevent hardcoded URL deployment
- [ ] **Documentation updated**: Team has access to troubleshooting guides

## CI/CD Guardrails

### Build-Time Validation
```yaml
# GitHub Actions example
- name: Validate Frontend Build
  run: |
    cd app/frontend/panel
    VITE_API_BASE_URL='/api/v1' npm run build
    
    echo "Checking for hardcoded localhost URLs..."
    if grep -r '"http://localhost:8001' dist/ | grep -v '\.map'; then
        echo "❌ Found hardcoded localhost URLs in production build"
        exit 1
    fi
    echo "✅ Build validation passed"
```

### Deployment Smoke Test
```yaml
# GitHub Actions example  
- name: CORS Smoke Test
  run: |
    echo "Testing CORS configuration..."
    curl -f -X OPTIONS "${{ secrets.PROD_HOST }}/api/v1/users/me" \
      -H "Origin: ${{ secrets.PROD_HOST }}" \
      -H "Access-Control-Request-Method: GET" \
      -H "Access-Control-Request-Headers: Authorization"
    echo "✅ CORS smoke test passed"
```

### Automated Guardrails Integration
```bash
# Add to CI pipeline
./ops/scripts/ci_guardrails.sh $PRODUCTION_HOST

# With strict mode (fail on warnings)
STRICT=1 ./ops/scripts/ci_guardrails.sh $PRODUCTION_HOST
```

### Optional Monitoring
```bash
# Set up log monitoring for CORS errors
grep -c "OPTIONS.*400" /var/log/nginx/access.log
grep -c "Disallowed CORS origin" /var/log/app/backend.log

# Alert if counts exceed thresholds
```

## Rollback Procedures

### Emergency Rollback (5-10 minutes)

#### Frontend Rollback
```bash
# Option 1: Restore previous build backup
cp -r /backup/panel-dist-previous/* /var/www/html/panel/

# Option 2: Quick rebuild without environment variable
cd app/frontend/panel
npm run build  # Uses default localhost for development
cp -r dist/* /var/www/html/panel/
```

#### Backend Rollback
```bash
# Revert app/api/main.py CORS origins to previous state:
cors_origins = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
    # Remove production origins if causing issues
]

# Restart backend service
systemctl restart china-car-parts-api
```

#### Nginx Rollback
```bash
# If nginx config was modified
cp /etc/nginx/sites-available/default.backup /etc/nginx/sites-available/default
nginx -t && nginx -s reload
```

### Rollback Verification
```bash
# Verify development environment still works
curl -i -X OPTIONS 'http://localhost:8001/api/v1/users/me' \
  -H 'Origin: http://localhost:5173' \
  -H 'Access-Control-Request-Method: GET'

# Expected: 200 OK with proper CORS headers
```

### Post-Rollback Actions
1. **Identify root cause** of the issue that required rollback
2. **Update diagnostic documentation** with new findings
3. **Plan remediation** with additional testing
4. **Communicate status** to team and stakeholders

## Appendix

### Script Parameter Usage

#### HOST Parameter Examples
```bash
# Basic usage
./ops/scripts/smoke_cors.sh http://5.223.41.154

# With environment variables
export HOST="http://5.223.41.154"
export USERNAME="admin"
export PASSWORD="your_password"
./ops/scripts/smoke_cors.sh

# Production HTTPS (future)
./ops/scripts/smoke_cors.sh https://yourapp.com
```

#### CI Guardrails Usage
```bash
# Basic validation
./ops/scripts/ci_guardrails.sh http://5.223.41.154

# Custom dist directory
DIST_DIR=custom/build ./ops/scripts/ci_guardrails.sh http://5.223.41.154

# Strict mode (fail on warnings)
STRICT=1 ./ops/scripts/ci_guardrails.sh http://5.223.41.154
```

### Environment-Specific Notes

#### Staging vs Production Origins
- **Staging**: Use staging domain in CORS origins
- **Production**: Use production IP/domain in CORS origins  
- **Never**: Mix staging and production origins in same environment

#### HTTP vs HTTPS Considerations
- **Current**: HTTP-only deployment (`http://5.223.41.154`)
- **Future**: HTTPS migration requires both HTTP and HTTPS origins during transition
- **Best Practice**: Use relative URLs to automatically match page scheme

#### Mixed Content Prevention
- Relative URLs (`/api/v1`) automatically use same scheme as page
- Avoid absolute HTTP URLs when serving HTTPS pages
- Plan HTTPS migration for both frontend and backend simultaneously

### Security Considerations

#### CORS with Credentials
```python
# Only use with specific origins (never with "*")
allow_credentials=True   # Use only if cookies/sessions required
allow_origins=["*"]      # Never combine with allow_credentials=True
```

#### Header Security
```python
# Prefer specific headers over wildcards in production
allow_headers=["Authorization", "Content-Type"]  # Recommended
allow_headers=["*"]                              # Use cautiously
```

#### Monitoring Best Practices
- Monitor OPTIONS 4xx response rates
- Track authentication failure spikes
- Alert on asset serving failures
- Log CORS policy violations for security review

---

**Remember**: This runbook provides **recommended procedures**. Teams should adapt steps according to their specific deployment processes and security requirements.