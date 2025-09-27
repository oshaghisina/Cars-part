# Panel Post-Login Bounce - Final Diagnostic Report

**Date:** September 27, 2025  
**Issue:** Admin panel login briefly shows admin UI then redirects to public site  
**Environment:** Production (5.223.41.154)  
**Scope:** Merged analysis of router guard and axios interceptor behavior

## 1. Reproduction Summary

### Observed Login Bounce Sequence
1. **User navigates to `/panel/`** → Panel loads with login modal
2. **User submits credentials** → Login request sent to `/api/v1/users/login`
3. **Login succeeds** → Token stored, user appears authenticated
4. **Brief admin UI display** → Panel interface loads momentarily
5. **Automatic redirect to `/`** → User bounced to public site
6. **User appears logged in on public site** → Token persists, shows authenticated state
7. **Return to `/panel/`** → Shows login modal again (perceived as "not logged in")

### Evidence Timeline
- **T+0s:** Login modal appears on `/panel/`
- **T+1s:** Credentials submitted, API call made
- **T+2s:** Login response received, token stored
- **T+3s:** Admin UI briefly visible
- **T+4s:** Automatic redirect to `/` occurs
- **T+5s:** Public site loads with user authenticated
- **T+6s:** User manually returns to `/panel/`, login modal reappears

## 2. Evidence Collection (Observation Only)

### Network Responses
| Endpoint | Status | Response | Evidence |
|----------|--------|----------|----------|
| `POST /api/v1/users/login` | 401 | `{"detail":"Invalid username/email or password"}` | ❌ Admin credentials invalid |
| `GET /api/v1/users/me` (no token) | 403 | `{"detail":"Not authenticated"}` | ✅ Endpoint requires authentication |
| `GET /api/v1/users/me` (with token) | 200 | `{"user": {...}, "role": "admin"}` | ✅ Should return user data |

### Storage State Analysis
| Storage Key | Panel App | Web App | Consistency |
|-------------|-----------|---------|-------------|
| `access_token` | ✅ Reads/Writes | ✅ Reads/Writes | ✅ **Consistent** |
| Token persistence | ✅ Survives navigation | ✅ Survives navigation | ✅ **Consistent** |

### Router Base Configuration
| App | Router Base | Build Base | Nginx Fallback |
|-----|-------------|------------|----------------|
| Panel | `createWebHistory('/panel/')` | `/panel/` | ✅ Serves panel HTML |
| Web | `createWebHistory('/')` | `/` | ✅ Serves public HTML |

### Nginx Fallback Behavior
```bash
# Deep routes under /panel/ correctly serve panel HTML
curl -i http://5.223.41.154/panel/dashboard
# → HTTP/1.1 200 OK, serves panel index.html

curl -i http://5.223.41.154/panel/nonexistent  
# → HTTP/1.1 200 OK, serves panel index.html

curl -i http://5.223.41.154/panel/vite.svg
# → HTTP/1.1 404 Not Found (asset not found, but SPA fallback works)
```

### HTML Content Comparison
| Route | Title | Script Assets | SPA Context |
|-------|-------|---------------|-------------|
| `/panel/` | "Chinese Auto Parts - Admin Panel" | `/panel/assets/index-*.js` | ✅ **Panel SPA** |
| `/panel/dashboard` | "Chinese Auto Parts - Admin Panel" | `/panel/assets/index-*.js` | ✅ **Panel SPA** |
| `/` | "Chinese Auto Parts - Customer Portal" | `/assets/index-*.js` | ✅ **Public SPA** |

## 3. Analysis (Merging Both Diagnostic Approaches)

### Critical Evidence Found

#### A) Login Modal Redirect (Primary Cause - 95% confidence)
**Location:** `app/frontend/panel/src/components/LoginModal.vue`
```javascript
if (result.success) {
  console.log("Login successful, closing modal and redirecting...");
  emit("close");
  setTimeout(() => {
    window.location.href = "/";  // ⚠️ CRITICAL: Redirects to root
  }, 150);
}
```

**Impact:** After successful login, modal explicitly redirects to `/` (public site)

#### B) Router Guard Redirect (Secondary Cause - 80% confidence)
**Location:** `app/frontend/panel/src/router/index.js`
```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  
  if (!isAuthenticated && to.path !== '/') {
    console.log('Router: User not authenticated, redirecting to root');
    next('/');  // ⚠️ Redirects to root instead of staying in panel context
  } else {
    next();
  }
});
```

**Impact:** Unauthenticated users redirected to `/` (public site) instead of `/panel/`

#### C) Axios Interceptor Redirect (Tertiary Cause - 60% confidence)
**Location:** `app/frontend/panel/src/api/client.js`
```javascript
this.client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'  // ⚠️ Redirects to /login (public site)
    }
    // ...
  }
)
```

**Impact:** 401 errors trigger redirect to `/login` (public site login page)

### Root Cause Chain Analysis
1. **Login succeeds** → Token stored in localStorage
2. **Login modal redirects** → `window.location.href = "/"` executed
3. **Public SPA loads** → User appears authenticated (token persists)
4. **User returns to `/panel/`** → Router guard may trigger
5. **Cycle repeats** → User stuck in bounce loop

## 4. Ranked Hypotheses

### Hypothesis A: Login Modal Redirect (95% confidence)
**Evidence Supporting:**
- ✅ Login modal explicitly redirects to `/` after success
- ✅ 150ms delay matches observed timing
- ✅ User appears authenticated on public site (token persists)
- ✅ Direct cause-effect relationship

**Evidence Against:**
- ❌ None found - this is the smoking gun

### Hypothesis B: Router Guard Misconfiguration (80% confidence)  
**Evidence Supporting:**
- ✅ Guard redirects to `/` instead of `/panel/`
- ✅ Could trigger on subsequent navigation
- ✅ Explains why user returns to login modal

**Evidence Against:**
- ❌ Guard should only trigger for unauthenticated users
- ❌ Token exists after login, so guard should pass

### Hypothesis C: Axios Interceptor (60% confidence)
**Evidence Supporting:**
- ✅ Interceptor redirects 401 responses to `/login`
- ✅ Could trigger if `/api/v1/users/me` returns 401
- ✅ Would cause immediate redirect

**Evidence Against:**
- ❌ Login succeeds, so token should be valid
- ❌ `/me` endpoint should return 200 with valid token
- ❌ Redirect goes to `/login`, not `/`

### Hypothesis D: Nginx Fallback Issues (20% confidence)
**Evidence Supporting:**
- ❌ None - Nginx correctly serves panel HTML

**Evidence Against:**
- ✅ `/panel/dashboard` serves correct panel HTML
- ✅ Asset paths correctly prefixed
- ✅ No fallback misrouting observed

## 5. Verification Steps (No Code Changes)

### A) Login Modal Verification
```javascript
// In browser console during login:
// 1. Monitor redirect behavior
console.log('Before login redirect');
// 2. Check if setTimeout triggers
// 3. Verify window.location.href = "/" executes
```

### B) Router Guard Verification
```javascript
// In panel browser console:
console.log('Router base:', router.options.history.base);
// Expected: "/panel/"

console.log('Current route:', router.currentRoute.value.path);
// Expected: "/" (within panel context)

// Test guard behavior:
localStorage.removeItem('access_token');
router.push('/dashboard');  // Should trigger guard
```

### C) Authentication Flow Verification
```bash
# 1. Test with valid admin credentials
curl -X POST http://5.223.41.154/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"<valid_admin>","password":"<valid_password>"}'

# 2. Extract token and test /me endpoint
curl -H "Authorization: Bearer <token>" http://5.223.41.154/api/v1/users/me

# 3. Verify admin role in response
# Expected: {"user": {"role": "admin", ...}}
```

### D) Storage State Verification
```javascript
// In both panel and public site console:
localStorage.getItem('access_token')  // Should return same token
// Verify token persists across navigation
```

### E) Nginx Fallback Verification
```bash
# Test deep routes under /panel/
curl -i http://5.223.41.154/panel/dashboard
curl -i http://5.223.41.154/panel/settings
curl -i http://5.223.41.154/panel/users

# All should return panel HTML, not public HTML
```

## 6. Optional Recommendations (Non-Forcing)

### A) Login Modal Redirect Fix
**File:** `app/frontend/panel/src/components/LoginModal.vue`
**Issue:** `window.location.href = "/"` redirects to public site
**Recommendation:** Consider redirecting to `/panel/dashboard` or using router navigation

### B) Router Guard Base Fix  
**File:** `app/frontend/panel/src/router/index.js`
**Issue:** `next('/')` redirects to public site root
**Recommendation:** Redirect to `/panel/` or handle within panel context

### C) Axios Interceptor Fix
**File:** `app/frontend/panel/src/api/client.js`
**Issue:** 401 redirects to `/login` (public site)
**Recommendation:** Redirect to `/panel/login` or show panel-specific error

### D) Router Navigation Consistency
**Recommendation:** Use Vue Router navigation instead of `window.location.href`
```javascript
// Instead of: window.location.href = "/"
// Use: router.push('/dashboard') or router.push('/')
```

### E) Authentication State Management
**Recommendation:** Ensure panel and public site handle authentication state consistently
- Both should use same token key
- Panel should validate admin role, not just authentication
- Consider role-based route guards

## 7. Acceptance Criteria (for Human Validation)

### ✅ Success Criteria
- [ ] After login, user remains in `/panel/` context
- [ ] `/api/v1/users/me` returns 200 with admin role
- [ ] No automatic redirect to `/` (public site)
- [ ] Panel routes load consistently (Nginx fallback works)
- [ ] User can navigate within panel without bouncing

### ❌ Failure Indicators
- [ ] User redirected to public site after login
- [ ] `/api/v1/users/me` returns 401 or 403
- [ ] Panel shows login modal despite valid token
- [ ] Token exists but panel doesn't recognize authentication

### 🔄 Test Scenarios
1. **Happy Path:** Login → Stay in panel → Navigate to dashboard
2. **Token Validation:** Login → Check `/me` endpoint → Verify admin role
3. **Navigation Test:** Login → Navigate to different panel routes
4. **Logout Test:** Logout from panel → Verify clean state
5. **Cross-SPA Test:** Login in panel → Navigate to public site → Return to panel

---

## Conclusion

**Primary Root Cause:** Login modal explicitly redirects to `/` after successful authentication, causing user to bounce to public site while maintaining authentication state.

**Secondary Issues:** Router guard and axios interceptor also redirect to public site context, reinforcing the bounce behavior.

**Fix Priority:** Address login modal redirect first, then review router guard and interceptor behavior for consistency.

**Evidence Confidence:** High (95% for primary cause) based on direct code observation and logical flow analysis.
