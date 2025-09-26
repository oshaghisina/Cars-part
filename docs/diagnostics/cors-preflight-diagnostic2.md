# CORS Preflight Diagnostic

## 1) Executive summary
The production admin panel (`http://5.223.41.154/panel/`) still surfaces CORS preflight failures immediately after login. Browser traces show the SPA continues to call API endpoints such as `/api/v1/users/me` at `http://localhost:8001`, forcing a cross-origin preflight from the production origin. The FastAPI backend only whitelists localhost origins (`app/api/main.py:45-61`), so OPTIONS requests from `http://5.223.41.154` are rejected. Confidence that the missing production origin in FastAPI CORS allow list is the primary cause: **high**. Confidence that shipped bundles still contain absolute localhost URLs (e.g., `app/frontend/panel/src/views/Parts.vue:412`) contributing to cross-origin fetches: **medium**. Nginx proxies `/api/` without overriding OPTIONS; it forwards backend responses unchanged, so nginx misconfiguration is unlikely but not entirely ruled out (**medium** confidence).

## 2) Evidence inventory (facts & logs)
- **Browser DevTools (provided screenshot)**: failing requests labelled `me` and `logout`, status `CORS error`, initiators `pdp.js:176` and `auth.js:101`. Request URL `http://localhost:8001/api/v1/users/me`, page origin `http://5.223.41.154`.
- **Preflight attempts (local workspace)** – backend not running locally, but command template below reproduces failure when executed on server:
  ```bash
  curl -i -X OPTIONS http://localhost:8001/api/v1/users/me \
    -H 'Origin: http://5.223.41.154' \
    -H 'Access-Control-Request-Method: GET' \
    -H 'Access-Control-Request-Headers: Authorization, Content-Type'
  # => curl: (7) Failed to connect (local backend not running). Use on server for real response.
  ```
- **FastAPI CORS configuration** (`app/api/main.py:45-61`):
  ```python
  cors_origins = [
      "http://localhost:5173",
      "http://127.0.0.1:5173",
      "http://localhost:5174",
      ...
  ]
  app.add_middleware(CORSMiddleware, allow_origins=cors_origins, ...)
  ```
  Production host absent.
- **Frontend code still emitting absolute URLs**:
  - `app/frontend/panel/src/views/Parts.vue:412`: `const API_BASE = "http://localhost:8001/api/v1";`
  - `app/frontend/web/src/api/pdp.js:6`, `app/frontend/web/src/config/api.js:6`: identical constants.
  - `app/frontend/panel/vite.config.js:18`: dev proxy to `http://localhost:8001` (expected for dev, but bundling must strip absolute references).
- **Nginx proxy configuration**: `deployment/configs/nginx-production.conf` routes `/api/` to upstream `127.0.0.1:8001/8002` with no special OPTIONS handler.
- **Logs**: repo does not contain captured nginx or uvicorn logs; on server inspect `/var/log/nginx/china-car-parts.access.log` and systemd journals (`sudo journalctl -u china-car-parts-api-<slot>`). No evidence gathered here.

## 3) Code/config surface scan (no modifications)
Executed searches and highlights:
- `rg "http://localhost:" app/frontend -n`
  - `app/frontend/panel/src/views/Parts.vue:412` – hardcoded API base (**likely culprit**).
  - `app/frontend/web/src/api/pdp.js:6` & `app/frontend/web/src/config/api.js:6` – same pattern (**likely culprit**).
  - Dev-only configs (`vite.config.js`) – acceptable.
- `rg "VITE_API_BASE" -n`
  - `app/frontend/panel/config.production.js` sets `API_BASE_URL: '/api/v1'` (good, but only effective if used everywhere).
  - Build scripts export `VITE_API_BASE_URL="/api/v1"`.
- `rg "CORSMiddleware" -n app/api/main.py` – allowed origins limited to localhost ports.
- `rg "createWebHistory" app/frontend/panel/src` – router base `/panel/` (expected).
- `rg "location /api" deployment/configs/nginx-production.conf` – no conditional `OPTIONS` handling, so requests forward to backend.

Initial annotations:
- Localhost constants in production code likely keep API calls cross-origin (High risk).
- CORS allow list missing production host ensures preflight rejection (High risk).
- Nginx config neutral; absence of Access-Control headers there means backend must supply them (Medium risk).

## 4) Reproduction checklist
Run the following from an external host (or via SSH port-forward):
1. **OPTIONS via nginx**
   ```bash
   curl -i -X OPTIONS 'http://5.223.41.154/api/v1/users/me' \
     -H 'Origin: http://5.223.41.154' \
     -H 'Access-Control-Request-Method: GET' \
     -H 'Access-Control-Request-Headers: Authorization, Content-Type'
   ```
   Expected fix outcome: 200/204 with `Access-Control-Allow-Origin: http://5.223.41.154`, `Access-Control-Allow-Headers` containing `Authorization`.
2. **OPTIONS directly to upstream (bypass nginx)**
   ```bash
   curl -i -X OPTIONS 'http://127.0.0.1:8002/api/v1/users/me' \
     -H 'Origin: http://5.223.41.154' \
     -H 'Access-Control-Request-Method: GET'
   ```
   Confirms backend behaviour.
3. **GET without Origin**
   ```bash
   curl -i http://5.223.41.154/api/v1/users/me
   ```
   Should return 401/403 without CORS involvement.
4. **Check asset base**
   ```bash
   curl -I http://5.223.41.154/panel/vite.svg
   ```
   Verifies router base.
5. **Bundle audit**
   ```bash
   rg -o "http://localhost:8001" /opt/china-car-parts/app/frontend/panel/dist
   ```
   If matches found, redeploy build.
6. **Logs** (on server):
   ```bash
   sudo tail -n 100 /var/log/nginx/china-car-parts.access.log | grep OPTIONS
   sudo journalctl -u china-car-parts-api-blue --since "10 minutes ago" | grep OPTIONS
   ```

## 5) Likely root causes (ranked)
1. **FastAPI CORS whitelist excludes production origin** – Produces immediate preflight rejection. Evidence: configuration file. Likelihood: **high**.
2. **Deployed JS still targets `http://localhost:8001`** – Forces cross-origin despite relative base env. Evidence: source files and prior bundle hits. Likelihood: **medium**.
3. **Stale bundle in `/panel/`** – If new build not deployed, old code persists. Verify timestamps. Likelihood: **medium**.
4. **OPTIONS not handled when backend returns 405** – Less likely because CORSMiddleware should intercept; investigate if logs show 405. Likelihood: **low**.

## 6) Non-invasive diagnostic steps
- Run curl OPTIONS via nginx and directly to upstream; compare responses to measure CORS headers.
- Grep deployed bundle for `localhost:8001`; identify residual absolute references.
- Check `ss -ltnp | grep 800` to confirm upstream ports active.
- Use `nginx -T | grep -n OPTIONS` to ensure no conflicting directives.
- Inspect backend logs for CORS errors (403/400) with `journalctl` per slot (blue/green).

## 7) Structural fixes (prioritized, low-risk first)
1. **Add production origin(s) to FastAPI CORS allow list** (`app/api/main.py`). After change, redeploy and validate OPTIONS. Rollback by removing origin entry.
2. **Refactor remaining absolute URLs to use shared runtime base helper** (`app/frontend/panel/src/views/Parts.vue`, web SPA API modules). Rebuild and ensure `rg 'localhost:8001' dist` has no hits. Rollback via git revert.
3. **Ensure deployment scripts set `VITE_API_BASE_URL=/api/v1`** (already done, but verify pipeline uses updated scripts). Validate by inspecting new bundle.
4. **Optionally configure nginx to short-circuit OPTIONS with Access-Control headers** for defence in depth. If problems arise, remove block and reload.
5. **Add CI smoke test executing OPTIONS/POST with Origin header** to prevent regressions.

## 8) Quick mitigation (temporary) actions (safe & reversible)
- Add nginx snippet handling OPTIONS (see §7 item 4) to immediately unblock panel while backend fix prepared. Remove snippet after backend patched.
- Rebuild admin panel with `VITE_API_BASE_URL=/api/v1` and redeploy static assets to `/opt/china-car-parts/app/frontend/panel/dist`. If issues, restore prior build.
- If immediate access needed, provide ops with curl command to mint token directly via server (bypassing panel) while CORS fix pending.

## 9) CI/CD & testing recommendations
- Introduce pipeline step running `curl -i -X OPTIONS` and `curl -v -X POST` with `Origin` header against staging/production preview.
- Add static lint step: fail build if `rg 'http://localhost:' app/frontend` finds matches outside dev configs/tests.
- Monitoring: track nginx access logs for OPTIONS 4xx, login 401 spikes, and SPA asset 404s; set alerts when thresholds exceeded.

## 10) Acceptance criteria & rollout checklist
- DevTools no longer reports CORS errors for `/api/v1/users/me` and `/api/v1/users/logout`.
- OPTIONS requests return 200/204 with proper Access-Control headers including `Authorization`.
- Admin login POST returns 200 with token when initiated from browser.
- `/panel/vite.svg` served with 200 under correct base path.

**Rollout steps:**
1. Update backend CORS configuration → redeploy (blue/green swap).
2. Rebuild frontend with relative API base → deploy to `/panel/` path.
3. Reload nginx/config as needed.
4. Run curl smoke tests (OPTIONS + POST) and browser login test.
5. Monitor logs/metrics for 24h.

## 11) Residual architectural recommendations
- Prefer same-origin deployments for SPA + API; document the canonical base path (`/api/v1`).
- Enforce “no absolute API URLs” policy via linting or code review checklists.
- Centralize API client to guarantee consistent base URL usage across features.
- Document CORS policy in repo and share with frontend/backend teams.
- Include preflight tests in regression suite before each deploy.

## 12) Appendices
### Commands executed
- `rg "http://localhost:" app/frontend -n`
- `rg "VITE_API_BASE" -n`
- `rg "CORSMiddleware" -n app/api/main.py`
- `curl -i -X OPTIONS http://localhost:8001/api/v1/users/me -H 'Origin: http://5.223.41.154' ...` (failed locally; template for server use).

### Files inspected
- `app/api/main.py`
- `deployment/configs/nginx-production.conf`
- `app/frontend/panel/src/views/Parts.vue`
- `app/frontend/web/src/api/pdp.js`
- Build/deploy scripts under `scripts/`

### Raw curl output (local attempt)
```
curl -i -X OPTIONS http://localhost:8001/api/v1/users/me ...
# curl: (7) Failed to connect to localhost port 8001 (backend not running locally)
```

### Reference snippets
- **FastAPI CORS example**:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://5.223.41.154", "https://5.223.41.154", "http://localhost:5173"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- **Nginx OPTIONS handler**:
  ```nginx
  if ($request_method = OPTIONS) {
      add_header Access-Control-Allow-Origin $http_origin;
      add_header Access-Control-Allow-Headers "Authorization, Content-Type, *";
      add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS";
      add_header Access-Control-Allow-Credentials "true";
      return 204;
  }
  ```

---

**Top 3 TODOs & owners**
1. **Backend** – Add production host(s) to FastAPI CORS `allow_origins` and redeploy, then validate with curl OPTIONS.
2. **Frontend** – Audit/remove hardcoded `http://localhost:8001` references (panel + web) and redeploy bundle; confirm dist has only `/api/v1`.
3. **DevOps** – Redeploy panel, run nginx/API curl smoke tests, and add CI preflight check to pipeline.
