# CORS Policy & Configuration Snippets

## Policy Summary

This document provides reference configurations and best practices for maintaining stable CORS behavior in the China Car Parts application. These are **recommendations** that teams can review and adapt based on their specific security requirements.

### Architectural Principles

1. **Prefer same-origin deployment**: Serve API and frontend from the same domain via nginx proxy to eliminate CORS complexity
2. **Use relative API URLs**: Frontend should use `/api/v1` base paths instead of absolute URLs
3. **Explicit origin allowlists**: FastAPI CORS middleware should list specific allowed origins, not wildcards
4. **Environment-based configuration**: CORS origins should be configurable per environment (dev/staging/prod)

### Security Guidelines

- **Credentials handling**: Use `allow_credentials=True` only when cookies or authentication headers are required
- **Header restrictions**: Prefer specific header lists over `allow_headers=["*"]` in production
- **Origin validation**: Never use `allow_origins=["*"]` with `allow_credentials=True`
- **Vary header**: Consider `Vary: Origin` when supporting multiple origins

## Reference Configuration Snippets

### FastAPI CORS Middleware (Backend)

#### Basic Production Configuration
```python
# app/api/main.py
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Environment-based CORS origins
def get_cors_origins():
    origins = []
    
    if settings.app_env == "development":
        origins.extend([
            "http://localhost:5173",    # Admin panel dev
            "http://127.0.0.1:5173",
            "http://localhost:5174",    # Web portal dev
            "http://127.0.0.1:5174",
            "http://localhost:3000",    # Alternative dev port
            "http://127.0.0.1:3000",
        ])
    
    if settings.app_env in ["staging", "production"]:
        # Add production domains
        if hasattr(settings, 'prod_host') and settings.prod_host:
            origins.extend([
                f"http://{settings.prod_host}",
                f"https://{settings.prod_host}",
            ])
        
        # Additional production domains
        if hasattr(settings, 'domain_name') and settings.domain_name:
            origins.extend([
                f"https://{settings.domain_name}",
                f"https://admin.{settings.domain_name}",
            ])
    
    return origins

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Only if using cookies/sessions
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type", 
        "Accept",
        "X-Requested-With",
        # Add other headers as needed
    ],
    max_age=600,  # Cache preflight for 10 minutes
)
```

#### Development-Only Permissive Configuration
```python
# For development environments only
if settings.app_env == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permissive for development
        allow_credentials=False,  # Must be False with wildcard origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

#### Debugging Configuration
```python
# Add logging for CORS decisions (temporary debugging)
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CORSLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        method = request.method
        
        if method == "OPTIONS":
            logging.info(f"CORS preflight: {method} {request.url} from {origin}")
        
        response = await call_next(request)
        
        if method == "OPTIONS":
            logging.info(f"CORS response: {response.status_code} with headers: {dict(response.headers)}")
        
        return response

# Add before CORSMiddleware
app.add_middleware(CORSLoggingMiddleware)
```

### Nginx Configuration

#### Basic Proxy Configuration (Recommended)
```nginx
server {
    listen 80;
    server_name your.production.host;
    
    # Frontend assets - Customer Portal
    location / {
        root /var/www/html/web;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Admin Panel
    location /panel/ {
        alias /var/www/html/panel/;
        try_files $uri $uri/ /panel/index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API Proxy (Critical - must forward OPTIONS)
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Optional: Add security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
    }
}
```

#### Optional: Nginx OPTIONS Fallback Handler
```nginx
# Use only if backend CORS fails
location /api/v1/ {
    # Handle OPTIONS preflight at nginx level (fallback)
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Max-Age' 600 always;
        return 204;
    }
    
    # Regular proxy for non-OPTIONS
    proxy_pass http://127.0.0.1:8001/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Frontend Configuration

#### API Base URL (Centralized)
```javascript
// app/frontend/panel/src/config/api.js
const getApiBaseUrl = () => {
  const envValue = import.meta.env.VITE_API_BASE_URL;
  
  if (envValue && envValue.trim()) {
    return envValue.trim().replace(/\/$/, ''); // Remove trailing slash
  }
  
  // Fallback to relative path for same-origin deployment
  return '/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

// Validation for development
if (import.meta.env.DEV && API_BASE_URL.includes('localhost:8001')) {
  console.warn('⚠️  Using hardcoded localhost URL in development mode');
}
```

#### Axios Client Configuration
```javascript
// app/frontend/panel/src/api/client.js
import axios from 'axios';
import { API_BASE_URL } from '../config/api.js';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;
```

## Linting & Build Hygiene

### ESLint Rule (Optional)
```javascript
// .eslintrc.js
{
  "rules": {
    "no-hardcoded-api-urls": ["error", {
      "patterns": [
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "https://localhost:8001"
      ],
      "message": "Use relative API paths (/api/v1) instead of hardcoded URLs"
    }]
  }
}
```

### Build Verification Script
```bash
#!/bin/bash
# scripts/verify-production-build.sh

echo "🔍 Verifying production build for CORS compliance..."

DIST_DIR=${1:-"app/frontend/panel/dist"}

if [ ! -d "$DIST_DIR" ]; then
    echo "❌ Distribution directory '$DIST_DIR' not found"
    exit 1
fi

# Check for hardcoded localhost URLs (excluding source maps)
HARDCODED_URLS=$(grep -r '"http://localhost:8001' "$DIST_DIR/" 2>/dev/null | grep -v '\.map' || true)

if [ -n "$HARDCODED_URLS" ]; then
    echo "❌ Found hardcoded localhost URLs in production build:"
    echo "$HARDCODED_URLS"
    echo ""
    echo "💡 Fix by rebuilding with: VITE_API_BASE_URL='/api/v1' npm run build"
    exit 1
fi

# Check for relative API paths
RELATIVE_PATHS=$(grep -r '/api/v1' "$DIST_DIR/" 2>/dev/null | grep -v '\.map' | wc -l)

if [ "$RELATIVE_PATHS" -gt 0 ]; then
    echo "✅ Production build verification passed"
    echo "   - No hardcoded localhost URLs found"
    echo "   - Relative API paths detected: $RELATIVE_PATHS references"
else
    echo "⚠️  Warning: No relative API paths found in build"
    echo "   This might indicate a configuration issue"
fi
```

### Package.json Integration
```json
{
  "scripts": {
    "build": "vite build",
    "build:production": "VITE_API_BASE_URL=/api/v1 vite build",
    "verify:build": "scripts/verify-production-build.sh",
    "build:verified": "npm run build:production && npm run verify:build"
  }
}
```

## Monitoring & Alerting

### Nginx Log Analysis
```bash
# Monitor CORS-related errors
tail -f /var/log/nginx/access.log | grep OPTIONS

# Count OPTIONS requests by status
awk '$9 ~ /^[45]/ && $6 ~ /OPTIONS/ {print $9}' /var/log/nginx/access.log | sort | uniq -c

# Monitor authentication failures
grep "POST.*users/login.*[45][0-9][0-9]" /var/log/nginx/access.log | tail -10
```

### Application Metrics
```python
# Example: Add metrics to FastAPI (optional)
from prometheus_client import Counter, Histogram

cors_requests = Counter('cors_requests_total', 'Total CORS requests', ['method', 'origin', 'status'])
cors_preflight_duration = Histogram('cors_preflight_duration_seconds', 'CORS preflight request duration')

# In CORS middleware or endpoint handlers
cors_requests.labels(method='OPTIONS', origin=origin, status=200).inc()
```

### Simple Alerting Thresholds
```bash
# Alert conditions (adjust thresholds as needed)
# - OPTIONS 4xx responses > 10 per minute
# - Authentication 401 responses > 5 per minute  
# - Panel asset 404s > 3 per minute

# Example log-based alert check
CORS_ERRORS=$(tail -1000 /var/log/nginx/access.log | grep "OPTIONS.*400" | wc -l)
if [ "$CORS_ERRORS" -gt 10 ]; then
    echo "ALERT: High CORS error rate detected"
fi
```

## Development Workflow

### Local Development Setup
```bash
# Start development servers with proxy
cd app/frontend/panel
npm run dev  # Uses vite proxy to localhost:8001

# Backend automatically allows localhost origins
# No CORS issues in development
```

### Staging Environment
```bash
# Build for staging
VITE_API_BASE_URL='/api/v1' npm run build

# Deploy and test
./ops/scripts/smoke_cors.sh https://staging.yourapp.com
```

### Production Deployment
```bash
# Build for production
cd app/frontend/panel
VITE_API_BASE_URL='/api/v1' npm run build

# Verify build
./scripts/verify-production-build.sh

# Deploy and validate
./ops/scripts/smoke_cors.sh http://5.223.41.154

# Add to CI pipeline
./ops/scripts/ci_guardrails.sh http://5.223.41.154
```

## Troubleshooting Guide

### Common Issues

#### 1. "Access to XMLHttpRequest blocked by CORS policy"
**Cause**: Frontend making cross-origin requests
**Solution**: Verify frontend uses relative `/api/v1` paths, rebuild if necessary

#### 2. "Response to preflight request doesn't pass access control check"
**Cause**: Backend CORS configuration doesn't include request origin
**Solution**: Add origin to `cors_origins` list in FastAPI middleware

#### 3. "Request header field Authorization is not allowed"
**Cause**: `allow_headers` doesn't include Authorization
**Solution**: Add "Authorization" to `allow_headers` list

#### 4. OPTIONS returns 405 Method Not Allowed
**Cause**: Backend endpoint doesn't support OPTIONS method
**Solution**: Ensure CORS middleware is properly configured and applied

### Diagnostic Commands
```bash
# Test CORS headers directly
curl -v -X OPTIONS 'http://HOST/api/v1/users/me' \
  -H 'Origin: http://HOST' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization'

# Check nginx proxy behavior
curl -v 'http://HOST/api/v1/health'

# Verify frontend build
grep -r 'localhost:8001' app/frontend/panel/dist/ | grep -v '\.map'
```

### Debug Mode Configuration
```python
# Temporary debugging middleware (development only)
@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    method = request.method
    
    if method == "OPTIONS":
        print(f"🔍 CORS DEBUG: {method} {request.url}")
        print(f"   Origin: {origin}")
        print(f"   Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    if method == "OPTIONS":
        print(f"   Response: {response.status_code}")
        print(f"   CORS Headers: {[h for h in response.headers.items() if 'access-control' in h[0].lower()]}")
    
    return response
```

## Environment-Specific Considerations

### Development Environment
- **CORS**: Permissive settings acceptable
- **Origins**: localhost with various ports
- **Assets**: Served by Vite dev server with proxy

### Staging Environment  
- **CORS**: Production-like configuration
- **Origins**: Staging domain(s) only
- **Assets**: Built and served by nginx

### Production Environment
- **CORS**: Minimal necessary permissions
- **Origins**: Explicit production domains only
- **Assets**: Optimized builds with proper caching

## Migration Path to HTTPS

### Preparation
```python
# Add HTTPS origins alongside HTTP
cors_origins = [
    "http://5.223.41.154",   # Current
    "https://5.223.41.154",  # Future HTTPS
]
```

### SSL Certificate Setup
```bash
# After SSL certificate installation
# Update nginx configuration for HTTPS
# Frontend will automatically use HTTPS for API calls (relative URLs)
```

### Mixed Content Prevention
- Use relative URLs (`/api/v1`) to automatically match page scheme
- Avoid absolute HTTP URLs when page is served over HTTPS
- Test all functionality after HTTPS migration

---

**Note**: All snippets are provided as **reference examples**. Teams should review, adapt, and test configurations according to their specific security requirements and deployment environment.
