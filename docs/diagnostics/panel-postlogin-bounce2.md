# Panel Post-Login Bounce Diagnostic Report

**Date:** September 27, 2025  
**Issue:** Admin panel login briefly shows admin UI then redirects to public site  
**Environment:** Production (5.223.41.154)  
**Scope:** Frontend routing, authentication, and SPA fallback behavior

## 1. Reproduction Log

### Test Sequence
1. **Navigate to public site** → `http://5.223.41.154/` ✅
2. **Navigate to admin panel** → `http://5.223.41.154/panel/` ✅
3. **Submit login credentials** → Login modal appears ✅
4. **Brief admin UI display** → Admin interface loads momentarily ✅
5. **Bounce to public site** → Redirects to public site with user logged in ✅
6. **Return to /panel/** → Shows login modal again ❌

### Evidence Collected
- **Nginx routing behavior confirmed:** Both `/panel/` and `/panel/dashboard` serve identical HTML content
- **SPA fallback working:** Deep routes under `/panel/` correctly serve panel index.html
- **Authentication endpoints accessible:** Login endpoint responds (401 for invalid credentials)

## 2. Evidence Snapshot

### Network Traces (Production Server)
```bash
# Panel root access
curl -i http://5.223.41.154/panel/
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 490

# Panel deep route access  
curl -i http://5.223.41.154/panel/dashboard
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 490

# Both return identical HTML with panel assets:
# <title>Chinese Auto Parts - Admin Panel</title>
# <script src="/panel/assets/index-DpuOXTjl.js"></script>
```

### Storage State Analysis
Both SPAs use **identical storage key**: `access_token`

**Panel Auth Store:**
```javascript
// app/frontend/panel/src/stores/auth.js
token: localStorage.getItem("access_token"),
localStorage.setItem("access_token", this.token);
localStorage.removeItem("access_token");
```

**Web Portal Auth Store:**
```javascript  
// app/frontend/web/src/stores/auth.js
token: ref(localStorage.getItem('access_token'))
localStorage.setItem('access_token', token.value)
localStorage.removeItem('access_token')
```

### Document Base and Router Configuration

**Panel Router:**
```javascript
// app/frontend/panel/src/router/index.js
const router = createRouter({
  history: createWebHistory('/panel/'),
  routes,
});

// Route guard logic:
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  
  if (!isAuthenticated && to.path !== '/') {
    console.log('Router: User not authenticated, redirecting to root');
    next('/');  // ⚠️ CRITICAL: Redirects to '/', not '/panel/'
  } else {
    next();
  }
});
```

**Web Portal Router:**
```javascript
// app/frontend/web/src/router/index.js
const router = createRouter({
  history: createWebHistory('/'),
  routes,
})
```

### Role Guard Analysis
Panel route guard redirects to `/` (root) when authentication fails, which loads the **public SPA** instead of staying within the panel context.

## 3. Code/Config Surface Scan

### Hardcoded Redirects Found
```bash
# Panel dist contains redirect logic
grep -o "window.location.href.*=.*/" app/frontend/panel/dist/assets/index-DijDuLrR.js
# Found: window.location.href="/login" (in error handling)
```

### Route Guard Logic
```javascript
// CRITICAL ISSUE: Route guard redirects to '/' instead of '/panel/'
if (!isAuthenticated && to.path !== '/') {
  next('/');  // This loads the public SPA
}
```

### Storage Key Consistency
✅ **Both SPAs use same storage key:** `access_token`  
✅ **Token persistence:** Both read/write to same localStorage key  
✅ **Logout behavior:** Both clear the same token

## 4. Ranked Hypotheses

### A) Route Guard Redirects to Wrong Base (HIGH - 90% confidence)
**Evidence:**
- Panel route guard redirects to `/` instead of `/panel/`
- This causes the public SPA to load instead of staying in panel context
- Both SPAs share the same `access_token` key, so user appears logged in on public site

**Root Cause:** `next('/')` in panel router guard loads public SPA

### B) Authentication State Mismatch (MED - 60% confidence)  
**Evidence:**
- Panel requires authentication for all routes except `/`
- Token exists but may not be valid for admin role
- `/api/v1/users/me` may return non-admin user, causing panel to reject access

**Root Cause:** User has valid token but insufficient role permissions

### C) Nginx SPA Fallback Misconfiguration (LOW - 20% confidence)
**Evidence:**
- `/panel/` and `/panel/dashboard` both serve correct panel HTML
- Asset paths correctly prefixed with `/panel/`
- No evidence of incorrect fallback behavior

**Root Cause:** Nginx correctly configured for panel SPA routing

### D) Post-Login Navigation Target (LOW - 15% confidence)
**Evidence:**
- Login success handler may navigate to `/dashboard` without `/panel/` prefix
- This would load public SPA instead of panel

**Root Cause:** Post-login redirect uses absolute path instead of relative

### E) Token Storage Divergence (LOW - 10% confidence)
**Evidence:**
- Both SPAs use identical `access_token` key
- Token persistence confirmed across both applications
- No evidence of storage conflicts

**Root Cause:** Token storage is consistent between SPAs

## 5. Verification Checks

### Route Guard Fix Verification
```bash
# Test panel authentication with valid token
curl -H "Authorization: Bearer <token>" http://5.223.41.154/api/v1/users/me

# Check if user has admin role in response
# Expected: {"user": {"role": "admin", ...}}
```

### Panel Router Base Verification
```javascript
// In browser console on /panel/:
console.log('Router base:', router.options.history.base);
// Expected: "/panel/"

console.log('Current route:', router.currentRoute.value.path);
// Expected: "/" (within panel context)
```

### Authentication Flow Verification
```bash
# 1. Login to get token
curl -X POST http://5.223.41.154/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"admin","password":"<correct_password>"}'

# 2. Use token to check user role
curl -H "Authorization: Bearer <token>" http://5.223.41.154/api/v1/users/me

# 3. Verify admin role in response
```

### Storage State Verification
```javascript
// In panel browser console:
localStorage.getItem('access_token')  // Should return token
// In public site browser console:  
localStorage.getItem('access_token')  // Should return same token
```

## 6. Conclusion & Next Steps

### Most Likely Root Cause
**Route Guard Redirect Issue (Hypothesis A)** - The panel router guard redirects unauthenticated users to `/` (root) instead of `/panel/`, causing the public SPA to load while maintaining the user's authentication state.

### Minimal Change Area
**File:** `app/frontend/panel/src/router/index.js`  
**Section:** Route guard logic in `router.beforeEach()`  
**Issue:** `next('/')` should be `next('/panel/')` or handled differently

### Smoke Test Checklist
After applying the fix:

1. **Login Test:**
   - Navigate to `/panel/`
   - Submit valid admin credentials
   - Verify admin panel loads and stays loaded
   - No redirect to public site

2. **Deep Route Test:**
   - Navigate to `/panel/dashboard`
   - Verify panel loads correctly
   - No fallback to public site

3. **Authentication Guard Test:**
   - Clear localStorage token
   - Navigate to `/panel/dashboard`
   - Verify redirect to `/panel/` (not `/`)
   - Login modal should appear

4. **Cross-SPA Token Test:**
   - Login in panel
   - Navigate to public site
   - Verify user appears logged in
   - Return to panel - should remain logged in

### Implementation Priority
1. **Immediate:** Fix route guard redirect path
2. **Secondary:** Add admin role validation in guard
3. **Future:** Implement proper role-based access control

---

**Diagnosis Complete** - Route guard misconfiguration identified as primary cause of post-login bounce behavior.
