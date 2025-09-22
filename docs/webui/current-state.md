**Current Web UI/API/Proxy/CI Setup**

- Admin SPA is a Vue 3 + Vite app at `app/frontend/panel` with no explicit base configured; it assumes mounting at site root (`/`). Nginx serves the built `dist` at `/`, and proxies API traffic under `/api/*` to FastAPI upstreams. CI currently runs frontend tests/lint but does not build/upload frontend artifacts; staging/production build behavior varies by script vs. workflow.

**Admin SPA Mount**
- Router base: history uses default base `/`.
  - `app/frontend/panel/src/router/index.js:63`
- Vite base: not set (defaults to `/`).
  - Add near `export default defineConfig({ ... })` if mounting under a subpath (e.g., `/admin/`). `app/frontend/panel/vite.config.js:5`
- Dev server proxy: `/api` → `http://localhost:8001`.
  - `app/frontend/panel/vite.config.js:16`
- Dev server port: 5173.
  - `app/frontend/panel/vite.config.js:13`
- Build output directory: `dist` (relative to `app/frontend/panel`).
  - `app/frontend/panel/vite.config.js:24`
- Nginx serves SPA from `dist` at site root with HTML5 history fallback:
  - `deployment/configs/nginx-production.conf:86` and `deployment/configs/nginx-staging.conf:69`

**API Surface and Health**
- FastAPI app mounts versioned routers under `/api/v1/*`:
  - Search `/api/v1/search`: `app/api/main.py:54`
  - Bulk `/api/v1/bulk`: `app/api/main.py:56`
  - Analytics `/api/v1/analytics`: `app/api/main.py:58`
  - AI Search `/api/v1/ai-search`: `app/api/main.py:60`
  - Wizard `/api/v1/wizard`: `app/api/main.py:62`
  - Orders `/api/v1/orders`: `app/api/main.py:63`
  - Leads `/api/v1/leads`: `app/api/main.py:64`
  - Parts `/api/v1/parts`: `app/api/main.py:65`
  - Vehicles `/api/v1/vehicles`: `app/api/main.py:66`
  - Categories `/api/v1/categories`: `app/api/main.py:68`
  - Users `/api/v1/users`: `app/api/main.py:70`
  - Admin `/api/v1/admin`: `app/api/main.py:71`
- Health checks:
  - Root health: `/health` `app/api/main.py:48`
  - Versioned health: `/api/v1/health` `app/api/main.py:78`
- CORS (backend): static allowlist for localhost dev ports only.
  - `app/api/main.py:33` through `app/api/main.py:45`
- Dev CORS/proxy (frontend): requests to `/api` proxied to `http://localhost:8001`.
  - `app/frontend/panel/vite.config.js:16`

**Reverse Proxy Stack**
- Nginx (production):
  - SPA at `/` with history fallback and long-lived asset caching.
    - `deployment/configs/nginx-production.conf:86` (root), `deployment/configs/nginx-production.conf:88` (fallback)
  - API upstream pool with ports 8001 primary / 8002 backup.
    - `deployment/configs/nginx-production.conf:11-17` (upstream), `/api/` proxy at `deployment/configs/nginx-production.conf:104-135`
  - Health proxy: `/health` proxies upstream.
    - `deployment/configs/nginx-production.conf:138-150`
- Nginx (staging):
  - SPA at `/` served from staging dist, fallback enabled.
    - `deployment/configs/nginx-staging.conf:69-71`
  - `/api/` proxy to `127.0.0.1:8001` upstream.
    - `deployment/configs/nginx-staging.conf:80-106`
  - Health proxy `/health` to upstream.
    - `deployment/configs/nginx-staging.conf:108-121`
- Blue/Green scripts/config patterns (two paradigms observed):
  - Config-file driven upstream named `china_car_parts_api` with primary/backup (`deployment/configs/nginx-production.conf`).
  - Script-generated upstreams named `blue-api`/`green-api` with site config pointing to a specific environment dir and port (`setup_production_blue_green.sh`).
- Caddyfile leftovers (not aligned with current Nginx stack): proxies `/api/*` to `localhost:8000` and mounts SPA under `/admin/*` with root redirect to `/admin/`.
  - `Caddyfile:1`, `/api/*` at `Caddyfile:6`, `/admin/*` at `Caddyfile:14`, redirect at `Caddyfile:30`

**CI/CD Overview**
- Active workflow: password-based CI/CD.
  - Frontend CI runs tests and lint; no build artifacts are uploaded.
    - `ci-frontend` job: `app/frontend/panel` tests/lint at `.github/workflows/main_password_auth.yml:73-103`
  - Staging deploy step pulls code, pip installs, alembic upgrade, restarts services; no frontend build invoked in the workflow step itself (separate staging script does build, see below).
    - `.github/workflows/main_password_auth.yml:165-219`
  - Production deploy (blue/green) restarts environment-specific systemd units and tries to switch Nginx upstream via `sed`.
    - `.github/workflows/main_password_auth.yml:239-337`
- Deployment scripts (server-side):
  - Production blue/green script builds frontend on the server, provisions systemd units per env, and toggles Nginx upstream port in config.
    - `deployment/scripts/blue-green-deploy.sh` (not run by Actions directly but intended for operator use)
  - Staging deploy script explicitly builds frontend on server before restarting services.
    - `deployment/scripts/deploy-staging.sh`
- Disabled workflows show prior intent to build frontend and upload artifacts for deployment, and more robust Nginx port rewrites.
  - `.github/workflows/cd-production.yml.disabled`
  - `.github/workflows/main.yml.disabled`

**Telegram Bot and Other Services**
- Telegram bot runs as systemd service alongside API in production, restarted on deployments.
  - Production unit template: `deployment/configs/china-car-parts-bot.service:16` (ExecStart uses `python -m app.bot.main`) and health check string `deployment/configs/china-car-parts-bot.service:42`. Current code’s module entry is `app.bot.bot`, not `app.bot.main`.
- No HTTP surface for the bot; no routing impact beyond service lifecycle during deployments.

**Observed Risks and Drift**
- SPA mount assumptions:
  - Router history base and Vite `base` both assume `/`. If mounting under `/admin`, both router and Vite base need updates; Nginx try_files is correct for history fallback.
- Frontend build in CI/CD:
  - Active GitHub workflow does not build/upload frontend artifacts and production workflow snippet does not run `npm run build` on server; depending on path used, SPA assets may go stale across deploys. Staging server script does build.
- Blue/green upstream mismatch:
  - Two Nginx paradigms exist: `china_car_parts_api` vs. `blue-api/green-api`. The production workflow’s CURRENT/TARGET detection and `sed` pattern at `.github/workflows/main_password_auth.yml:278-329` likely won’t match the `china_car_parts_api` config and the `grep|cut` logic returns `"upstream blue"` instead of `"blue"`.
- CORS drift:
  - Backend allows only localhost origins; safe if UI and API share the same origin (Nginx-proxied) but blocks cross-origin dev hitting remote API. Consider unifying with `settings.frontend_origin` in `app/core/config.py`.
- Dev port mismatch:
  - Vite proxies to `8001` (`vite.config.js:16`) but `scripts/start_api.sh` runs `uvicorn` on `8000` (`scripts/start_api.sh:17`). Local dev may require adjusting one side.
- Bot service ExecStart target:
  - Systemd unit template references `app.bot.main`; the code defines `app.bot.bot` as the module entry. Service would fail to start unless adjusted.

**Path Mapping Reference (Quick Lookup)**

| Page/Path                  | Nginx Location Block                                   | Build Output Directory                 |
|----------------------------|---------------------------------------------------------|----------------------------------------|
| `/`                        | `location / { root <env>/app/frontend/panel/dist; }`    | `app/frontend/panel/dist`              |
| `/panel/`                  | Not configured in Nginx (current)                       | `app/frontend/panel/dist` (if enabled) |
| `/api/v1/*`                | `location /api/ { proxy_pass http://china_car_parts_api; }` | n/a                                    |
| `/admin/* → /panel/*`      | Not configured in Nginx; legacy redirect exists in Caddy | n/a                                    |

**File → Purpose → Key Lines**
- `app/frontend/panel/src/router/index.js:63` → Router history base → change to `createWebHistory('/admin/')` if mounting under subpath.
- `app/frontend/panel/vite.config.js:5` → Vite base/location → add `base: '/admin/',` at top-level if needed; proxy at `app/frontend/panel/vite.config.js:16`; build outDir at `app/frontend/panel/vite.config.js:24`.
- `deployment/configs/nginx-production.conf:86` → SPA root path (`dist`) and fallback at `deployment/configs/nginx-production.conf:88`.
- `deployment/configs/nginx-production.conf:104` → API `/api/` proxy to upstream pool.
- `app/api/main.py:33` → CORS origins; health at `app/api/main.py:48` and `app/api/main.py:78`; router mounts `app/api/main.py:54-71`.
- `.github/workflows/main_password_auth.yml:73` → Frontend CI tests/lint; production blue/green swap logic at `.github/workflows/main_password_auth.yml:278-333`.
- `deployment/configs/china-car-parts-bot.service:16` → Bot ExecStart module path (should match `app.bot.bot`).
- `scripts/start_api.sh:17` → Dev API port 8000 (adjust to 8001 or change Vite proxy).

**Open Questions**
- Do we intend to mount the admin SPA at the site root in all envs, or under a subpath like `/admin`? If subpath, can we standardize Vite/Router base accordingly?
- Which Nginx paradigm is authoritative in production: `china_car_parts_api` upstream with port edits, or the script-generated `blue-api/green-api` config? Should we align the GitHub workflow’s swap logic to that?
- Should frontend builds be performed on the server during deploys or built in CI and shipped as artifacts? If artifacts, where should we publish and how should Nginx serve them?
- What are the canonical production/staging domains we should bake into CSP/CORS and health monitoring? Any shared-origin constraints we must uphold?
- Any SEO or analytics/tracking requirements for the admin SPA (e.g., GA, custom CSP) that affect asset base or headers?
- Do we need consistent cache headers for SPA HTML (e.g., short max-age) vs. static assets (immutable, long-lived) across staging/production?
- For local dev, should we standardize on API port 8001 (matching Vite proxy) or update Vite to 8000 to avoid confusion?

```mermaid
flowchart LR
  client[Client] --> nginx[Nginx reverse proxy]

  nginx -->|"/"| adminSPA[Admin SPA (served from app/frontend/panel/dist)]
  nginx -.->|"/panel/"| adminPanelAlt[Admin SPA (not configured; would require base '/panel')]
  nginx -->|"/api/v1/* (via location /api/)"| fastapi[FastAPI backend (uvicorn :8001 primary, :8002 backup)]
  nginx -->|"/admin/*"| redirect[301 redirect to /panel/* (legacy Caddy, not in Nginx)]
```
