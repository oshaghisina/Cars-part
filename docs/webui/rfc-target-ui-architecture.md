# RFC — Target UI Architecture: Dual SPAs on Same Origin with Nginx Blue/Green

## 1) Decision Summary

- Decision: Adopt Option A (Dual SPA on the same origin) as MVP.
  - Customer SPA is served at `/`.
  - Admin SPA is served at `/panel/`.
  - API remains stable at `/api/v1/*`.
- Scope and non‑goals:
  - No backend API surface changes (contract at `/api/v1/*` unchanged).
  - Same‑origin enforced in production/staging (no subdomains for MVP).
  - Do not introduce SSR/SSG or a service mesh.
  - Legacy Caddy config is not authoritative; Nginx is the single ingress.

## 2) Architecture Snapshot

```mermaid
flowchart LR
  client[Client] --> nginx[Nginx (blue/green)]
  nginx -->|"/"| webSPA[Customer SPA (web/dist)]
  nginx -->|"/panel/*"| adminSPA[Admin SPA (panel/dist)]
  nginx -->|"/api/v1/*"| api[FastAPI backend (8001/8002)]
  nginx -->|"/admin/*"| redirect[301 → /panel/*]
  redirect --> adminSPA
```

- History fallback rules:
  - `/` → try_files fallback to `/index.html` (Customer SPA).
  - `/panel/` → try_files fallback to `/panel/index.html` (Admin SPA).
- Redirects:
  - Permanent `/admin/* → /panel/*` (preserve path and query).

## 3) Config Changes (concise, actionable)

- Admin SPA
  - Router base: `createWebHistory('/panel/')`.
  - Vite base: `VITE_BASE=/panel/` (prod) with code using `base: process.env.VITE_BASE || '/'`.
  - Validate chunk/asset paths resolve under `/panel/` and deep links load.
- Customer SPA
  - Router/Vite base: `/`.
  - Build output separate from admin (e.g., `app/frontend/web/dist`).
- Nginx
  - Add two SPA blocks with history fallback: `/` → Customer dist; `/panel/` → Admin dist.
  - Add permanent redirect: `/admin/* → /panel/*`.
  - API proxy remains at `/api/v1/*` pointing to FastAPI upstream (blue on `:8001`, green on `:8002`).
- CI/CD
  - Build both SPAs in pipeline.
  - Publish both `dist` outputs to the blue/green target directories.
  - Smoke checks before cutover: `GET /`, `GET /panel/`, `GET /api/v1/health` (expect 200).

## 4) Caching & Performance

- HTML: short TTL with revalidation (e.g., 5–60 minutes), to ensure fresh shell after deploy.
- Static assets (hashed): long TTL (e.g., 1 year) with `immutable`.
- Target: cached TTFB < 1s at `/` (p90) in production; p95 API < 300ms for cached endpoints.
- Cache busting: content hashing + blue/green switch to minimize stale references.
- Optional CDN can honor the same headers; purge on deploy is not required if hashes are used.

## 5) Observability & Safety

- Synthetic checks: `GET /`, `GET /panel/`, `GET /api/v1/health` (pre‑ and post‑switch).
- Log/alert on SPA 404s and missing chunk loads; track SPA navigation error rate (<1%).
- Rate‑limit public POST endpoints (e.g., `/api/v1/leads`, `/api/v1/orders`) and login.
- Retain JWT for admin authentication; validate cookies/headers consistent with same‑origin policy.

## 6) Rollout & Backout

- Rollout (staging → production)
  1. Update Admin SPA base settings; build Admin SPA.
  2. Add Nginx `/panel` block and `/admin/* → /panel/*` redirect; reload Nginx in staging.
  3. Smoke test staging: `/`, `/panel/`, `/api/v1/health`; validate deep links and assets.
  4. Build Customer SPA and configure Nginx `/` block when ready.
  5. For production: deploy builds to the non‑active (blue/green) target; run health + smoke checks directly on that port.
  6. Switch Nginx upstream/roots to the new environment; re‑run smoke checks via LB.
- Backout
  - Revert Nginx pointer to the previous blue/green target and reload Nginx.
  - Ensure previous environment retains working SPA bundles (no need to rebuild for quick backout).
- Success criteria
  - All smoke checks pass; no elevated SPA 404s/missing chunks; admin authentication works under `/panel`.

## 7) Risks & Mitigations

- Asset base mismatches (wrong `base`/router base) → Mitigate with checklist, QA deep‑link tests, and 404 monitoring.
- History fallback gaps → Verify `try_files` rules for both `/` and `/panel/` before cutover.
- Config drift vs legacy Caddy → Remove or ignore Caddy; consolidate on Nginx; codify blocks in infra scripts.
- CI/CD not building both SPAs → Require explicit build steps and artifact publication for both bundles.

## 8) Acceptance Criteria

- `/` serves the Customer SPA with correct history fallback and assets.
- `/panel/` serves the Admin SPA with correct base, deep links, and assets.
- `/api/v1/*` proxy unaffected; `/api/v1/health` returns 200 pre/post cutover.
- `/admin/*` redirects to `/panel/*` (path/query preserved).
- Blue/green smoke tests pass before and after switch.

## 9) Open Questions (final blockers)

- SEO/analytics requirements for the Customer SPA at `/` (CSP allowances, sitemap, i18n locales)?
- CDN/Cloudflare in front of Nginx: required now or later; any specific cache/purge integration?
- TLS termination point(s): CDN, Nginx, or both; any mTLS/client‑cert requirements for admin/API?
- Cache purge process (if CDN present): automated hooks vs. rely on content hashing only?
- Any near‑term cross‑origin needs that would favor subdomains instead of same‑origin?

