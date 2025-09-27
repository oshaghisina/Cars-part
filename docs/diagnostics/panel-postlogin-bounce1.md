# Panel Post-Login Bounce Diagnostic

## 1) Reproduction Log
_Reproduce in a desktop browser with DevTools open (Network + Console tabs). Timestamps below illustrate the expected observation points; replace with real values during execution._

| Step | Action & timestamp | Observed URL | Notes / network events |
|------|-------------------|--------------|-------------------------|
| 1 | `T0` – Load https://5.223.41.154/ | `https://5.223.41.154/` | Public SPA renders. No redirects. |
| 2 | `T0+5s` – Navigate to `/panel/` (address bar or top nav) | `https://5.223.41.154/panel/` | Network should fetch `/panel/` (status 200). Panel bundle loads. |
| 3 | `T0+10s` – Submit admin credentials | stays on `/panel/` until bounce | Network log: `POST /api/v1/users/login` (expect 200) followed by `GET /api/v1/users/me`. |
| 4 | `T0+12s` – Admin layout briefly renders (`/panel/dashboard`) | URL briefly `https://5.223.41.154/panel/` or `/panel/dashboard` | Console logs from panel auth store: “Auth store: API response received … Authentication state updated”. |
| 5 | `T0+13s` – Browser navigates away automatically | Final URL `https://5.223.41.154/` (public SPA) | Network tab shows 30x? If redirected by JS, look for `window.location.href` change. Panel `/panel/me` requests show 401. Panel reopened now asks for login again. |

**Console capture:** During step 5, note any log lines referencing router guard (e.g., “Router: User not authenticated, redirecting to root”) and the `window.location.href = '/login'` assignment from the Axios interceptor.

## 2) Evidence Snapshot

### Network traces
- `POST https://5.223.41.154/api/v1/users/login`
  - Expected: `200 OK`, JSON payload `{ access_token: "…", user: { role, … } }`.
- `GET https://5.223.41.154/api/v1/users/me`
  - Actual (from user report): returns `401 Unauthorized` shortly after login.
  - Response headers lack `Access-Control-Allow-Origin` only because backend denies request.
  - Body (inspect via DevTools > Preview) contains error detail (e.g., `{"detail":"Not authenticated"}` or permission message).
- Any 30x after `/panel/*` navigation? Capture if present; otherwise note “No redirects, navigation triggered by JS”.

### Storage state
- **Panel** – After login succeeds but before bounce: `localStorage.getItem('access_token')` contains JWT. After bounce (public app loaded), token may still exist but panel guard sees logout event triggered by Axios interceptor.
- **Public site** – Uses the same key (`access_token`), so upon returning to `/` the site finds the token and shows “logged in” status (displays name in header).

### Document / router base
- Panel build uses `<base href="/panel/">` (verify in Elements panel). Router configured with `createWebHistory('/panel/')` (`app/frontend/panel/src/router/index.js:72-81`).
- Assets under `/panel/` respond 200:
  ```bash
  curl -I https://5.223.41.154/panel/vite.svg
  ```

### Role guard behaviour
- Panel router guard (`router.beforeEach` at `app/frontend/panel/src/router/index.js:85-97`) logs when token missing and redirects to `'/'` (with base `/panel/` this resolves to `/panel/`).
- Axios interceptor in `app/frontend/panel/src/api/client.js:26-47` removes `access_token` and executes `window.location.href = '/login'` on any 401.
- If `/api/v1/users/me` returns 401 (e.g., due to missing role), the interceptor forces full-page navigation to `/login`, which resolves to the public SPA route.

### Nginx curl probes (from any host)
```
curl -i https://5.223.41.154/panel/
curl -i https://5.223.41.154/panel/dashboard
curl -i https://5.223.41.154/
```
Expect both `/panel/` and `/panel/dashboard` to serve panel `index.html` (Content-Type `text/html`, includes `data-vite-dev-id` paths under `/panel/assets`). If `/panel/dashboard` serves the public index instead, note mismatch—currently config includes `try_files $uri $uri/ /panel/index.html;` so misroute is unlikely.

## 3) Code/Config Surface Scan (read-only)

| Search | Result (path:line) | Annotation |
|--------|--------------------|------------|
| `rg -n "window.location.href *= */" app/frontend/panel/dist` | No hits (after latest build) – check deployed bundle to confirm. | If panel dist still contains `/login`, update interceptor logic. |
| `rg -n "window.location.href" app/frontend/panel/src` | `src/api/client.js:40` → `window.location.href = '/login'`. | Causes full-page redirect to site root on 401. |
| `rg -n "router.push\(['"]\/" app/frontend/panel/dist` | Inspect results to ensure no hardcoded pushes to `/` (outside `/panel/`). | None observed in repo build. |
| `rg -n "beforeEach" app/frontend/panel/src` | `router/index.js:85` guard – only checks token presence. | Redirects to `/` (interpreted as `/panel/`). |
| `rg -n "localStorage.*access_token" app/frontend/panel/src` | `stores/auth.js`, `router/index.js` usage. | Panel shares token key with public SPA. |
| `rg -n "localStorage.*access_token" app/frontend/web/src` | `stores/auth.js` (same key). | Confirms shared storage. |

Files reviewed:
- `app/frontend/panel/src/api/client.js` – Axios interceptor redirect.
- `app/frontend/panel/src/router/index.js` – guard.
- `app/frontend/web/src/stores/auth.js` – shares storage key, explains why public site shows logged-in state.
- `deployment/configs/nginx-production.conf` – `/panel/` location uses `alias` and `try_files` fallback.

## 4) Ranked Hypotheses
1. **C) Route guard/role check redirect (401 path)** – **High confidence**. `/api/v1/users/me` likely returns 401 or a user without admin privileges; Axios interceptor clears token and redirects browser to `/login`, i.e., public site. Evidence: interceptor code + observed behaviour.
2. **D) Token storage divergence/clearing** – **Medium**. Interceptor removes token on 401, so panel loses auth state while public site still reads same key (if interceptor runs before redirect, key removed; but public site showing logged in indicates token might still exist). Verify by checking localStorage after bounce.
3. **B) Router base mismatch** – **Medium-Low**. Router uses correct base; no evidence of mismatch.
4. **A) Nginx SPA fallback misrouted** – **Low**. Config appears correct; confirm via curl `/panel/dashboard`.
5. **E) Post-login redirect target** – **Low**. No code pushing to `/dashboard` without base; guard shows `next('/')`, which resolves to `/panel/` due to base.

## 5) Verification Checks
- **Confirm /users/me response**:
  ```bash
  curl -i -H 'Authorization: Bearer <token>' https://5.223.41.154/api/v1/users/me
  ```
  Look for `role` field (e.g., `admin`). If 401 or non-admin role, supports hypothesis C.
- **Simulate interceptor effect**:
  In browser console (panel tab) run `localStorage.getItem('access_token')` before and after the bounce to see if token is removed by interceptor.
- **Verify nginx fallback**:
  ```bash
  curl -s https://5.223.41.154/panel/dashboard | head -n 5
  curl -s https://5.223.41.154/ | head -n 5
  ```
  Compare titles/markup; they should differ.
- **Check router base**: In panel console run `import.meta.env.BASE_URL` and `window.__VUE_ROUTER__?.options?.history?.base` (if exposed). Should both be `/panel/`.
- **Inspect response headers**: DevTools > Network > `/api/v1/users/me` → note status and JSON. If 200 but role not admin, guard may redirect elsewhere (confirm with guard logic).

## 6) Conclusion & Next Steps
Most probable root cause: the panel receives a 401/permission failure from `/api/v1/users/me`. The Axios interceptor responds by clearing the token and forcing `window.location.href = '/login'`, loading the public app. Because both SPAs share the `access_token` storage key, the public site reads the same token (if still present) and shows “logged in” even though the panel denies access.

**Recommended focus:**
- Verify `/users/me` response for the admin account to ensure role/permissions align with panel requirements.
- Review the interceptor redirect path (`client.js:32-43`) to avoid cross-app navigation; consider using router navigation within `/panel/` or presenting a guard message instead of redirecting to `/login`.

**Smoke checklist after fixes (to be executed manually):**
1. Log into `/panel/` → stay on `/panel/dashboard` without bounce.
2. Confirm `/api/v1/users/me` returns 200 with admin role.
3. Refresh `/panel/analytics` deep link – still loads panel shell.
4. Switch to public site – verify token persists only if desired; otherwise ensure isolation between SPAs.

---

_This report is observational only; no code/config changes were made._
