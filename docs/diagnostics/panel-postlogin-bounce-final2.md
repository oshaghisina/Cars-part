# Panel Post-Login Bounce – Consolidated Diagnostic

## 1. Reproduction Summary
| Step | Expected action | Observed URL & redirects | Storage state*
|------|-----------------|--------------------------|--------------|
| 1 | Load public site | `https://5.223.41.154/` (200) | `localStorage.access_token` empty
| 2 | Navigate to `/panel/` | `https://5.223.41.154/panel/` (200) | still empty
| 3 | Submit admin credentials | `/panel/` remains while `POST /api/v1/users/login` (200) followed by `GET /api/v1/users/me` (401) | token briefly set to JWT string
| 4 | Admin shell flashes (dashboard) | `router.currentRoute` shows `/` or `/dashboard` under `/panel/` | same token value
| 5 | Auto-bounce | Browser lands on `https://5.223.41.154/` (no 30x, triggered by JS) | token either cleared (if interceptor removed) or reused by public SPA (same key)

\*Storage observations derived from console logs (`Auth store: Authentication state updated`) and Axios interceptor behavior; verify via DevTools > Application > Local Storage.

## 2. Evidence Collection (Observation Only)
- **Network responses**
  - `POST /api/v1/users/login` → 200; payload `{ access_token, expires_in, user { role, ... } }` (per `app/frontend/panel/src/stores/auth.js` logging).
  - `GET /api/v1/users/me` immediately afterward → 401 (reported during reproduction, matches interceptor path for 401).
- **Storage keys** – Both panel and public SPA persist tokens in `localStorage` under `access_token` (`app/frontend/panel/src/stores/auth.js:18`, `app/frontend/web/src/stores/auth.js:13`).
- **Router/build base** – Panel router uses `createWebHistory('/panel/')` (`app/frontend/panel/src/router/index.js:72-81`); Vite config sets `base: process.env.VITE_BASE || '/'` with build script `VITE_BASE=/panel/`.
- **Guard & interceptor**
  - Router guard (`router.beforeEach`) logs “Router: User not authenticated, redirecting to root” and runs `next('/')` when token absent.
  - Axios interceptor (`app/frontend/panel/src/api/client.js:26-47`) on 401 removes `access_token` and executes `window.location.href = '/login'`.
- **Nginx fallback** – Config `deployment/configs/nginx-production.conf` shows `location /panel/ { alias ...; try_files $uri $uri/ /panel/index.html; }`, so `/panel/*` should fall back to panel index. Curl checks recommended below.

## 3. Analysis (Merged Findings)
- **Hypothesis A (from bounce1)**: `/api/v1/users/me` returns 401 (missing role/invalid token). Axios interceptor treats the response as unauthenticated, clears storage, and sets `window.location.href = '/login'`. Because the URL lacks `/panel/`, the browser loads the public SPA, giving the appearance of a redirect to the site. This explains the quick flash of the admin shell and the public site showing the user as logged in (token may still be cached or reissued by the public store).
- **Hypothesis B (from bounce2)**: Even without the interceptor, the router guard redirects unauthenticated users with `next('/')`. With router base `/panel/`, this should normally map to `/panel/`, but if the guard runs after the interceptor clears the token, the guard executes on the next navigation and resolves to `/` (public root). Both mechanisms together compound the bounce.
- **Additional considerations**: Router base appears correct; nginx fallback likely delivers `/panel/index.html` for deep routes. The primary triggers remain the 401 from `/users/me` and global redirection to `/login` (site-level path).

## 4. Ranked Hypotheses
| Hypothesis | Confidence | Evidence/notes | What would raise/lower confidence |
|------------|------------|----------------|----------------------------------|
| A) `/users/me` 401 triggers interceptor redirect to `/login` | **High** | Reproduction logs show 401; interceptor code explicitly redirects to `/login`. | Raise: capture Network tab confirming 401 + console showing `window.location.href = '/login'`. Lower: `/users/me` returns 200 with admin role. |
| B) Guard `next('/')` sends user to root when token missing | **Medium** | Guard logs “redirecting to root”; occurs after interceptor clears token. | Raise: console shows guard log just before bounce; `router.currentRoute` becomes `/`. Lower: guard disabled or token remains but bounce still occurs. |
| C) Nginx/router base misroute | **Low** | Config shows proper fallback; curl to `/panel/dashboard` should return panel index. | Raise: `curl` returns public index; check markup differences. |

## 5. Verification Steps (No Code Changes)
1. **Server tests**
   ```bash
   curl -I https://5.223.41.154/panel/
   curl -I https://5.223.41.154/panel/dashboard
   curl -I https://5.223.41.154/panel/vite.svg
   ```
   Expect panel assets/HTML for first two; 200 for SVG.
2. **API role check**
   After login, copy JWT and run:
   ```bash
   curl -i -H 'Authorization: Bearer <token>' https://5.223.41.154/api/v1/users/me
   ```
   Confirm status 200 and role includes `admin` (or required role). 401 confirms Hypothesis A.
3. **Console inspection**
   - `router.currentRoute.value.fullPath` after login (before bounce) to see intended path.
   - `localStorage.getItem('access_token')` before/after bounce to see if interceptor removed the token.
   - Watch console for logs “Auth store: Token validation failed” or “Router: User not authenticated...”.
4. **Interceptor observation**
   Set a breakpoint in DevTools (Sources → `client.js` at redirect line) to see trigger.

## 6. Optional Recommendations (Non-Forcing)
- Review panel router guard — consider redirecting to `/panel/login` (or dedicated route) rather than `/`.
- Review Axios interceptor — on 401, navigate within panel context or show modal instead of `window.location.href = '/login'`.
- Ensure `/api/v1/users/me` returns 200 for admin credentials; if permissions insufficient, adjust backend roles or panel requirements.
- Validate router/build base and nginx fallback during deployment to avoid cross-app navigation.

## 7. Acceptance Criteria for Human Validation
- Successful login keeps user on `/panel/…` routes; no automatic navigation to `/`.
- `/api/v1/users/me` returns 200 with expected admin role for panel session.
- Auth token persists in panel storage without being cleared (unless user logs out).
- `curl` checks confirm `/panel/*` routes serve panel bundle and do not fall back to public index.

---
_All findings are observational; no code or configuration changes were applied._
