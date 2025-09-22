# Implementation Plan — Two SPAs on Same Origin with Nginx Blue/Green

Incremental, non‑breaking rollout to serve Customer SPA at `/`, Admin SPA at `/panel/`, API at `/api/v1/*`, delivered via Nginx blue/green with smoke checks.

## 1) Milestones & Timeline

- M1 — Admin at /panel
  - Update Admin router base to `/panel/` and Vite base to `VITE_BASE=/panel/`.
  - Local build and deep‑link verification; document any base path issues.
- M2 — Customer SPA skeleton at /
  - Create minimal routes: Home, Search, Part Detail, Lead/Order, Track.
  - Local dev proxy to `/api`; local build sanity.
- M3 — Nginx config & redirects
  - Add `/` (Customer) and `/panel/` (Admin) SPA blocks with history fallback.
  - Add permanent redirect `/admin/* → /panel/*`; confirm path/query preserved.
- M4 — CI/CD builds & smoke
  - Pipeline builds both SPAs; publish `dist` outputs to blue/green targets.
  - Run smoke tests on target env before switch.
- M5 — Staging validation & UAT
  - Validate TTFB target, deep‑link checks, navigation error rate.
  - Stakeholder UAT sign‑off.
- M6 — Production cutover & monitoring
  - Blue/green switch after passing smoke checks.
  - Monitor and rehearse rollback.

## 2) Work Breakdown (files & actions)

- Admin SPA
  - Router base: `app/frontend/panel/src/router/index.js` → `createWebHistory('/panel/')`.
  - Vite base: `app/frontend/panel/vite.config.js` → `base: process.env.VITE_BASE || '/'` and set `VITE_BASE=/panel/` for prod.
  - Verify asset paths (CSS/IMG/Fonts) resolve from `/panel/`.
- Customer SPA (new)
  - Scaffold `app/frontend/web` with base router (`/`) and minimal routes (Home/Search/Part/Lead/Track).
  - Dev proxy to `/api`; ensure same‑origin assumption for prod.
- Nginx
  - Two SPA location blocks:
    - `/` → Customer dist + `try_files $uri $uri/ /index.html`.
    - `/panel/` → Admin dist + `try_files $uri $uri/ /panel/index.html`.
  - API proxy unchanged at `/api/v1/` (upstream :8001/:8002).
  - Redirect rule: `^/admin/(.*)$ → /panel/$1`.
  - Basic security headers and compression as in deployment spec.
- CI/CD
  - Update workflow to build both SPAs; publish artifacts to non‑active blue/green directory.
  - Add smoke checks: `GET /api/v1/health`, `GET /panel/`, `GET /` (with deep links).
  - Gate cutover on green smoke; add rollback step.
- Ops Hygiene
  - Standardize on Nginx; remove reliance on legacy Caddy config.
  - Align local dev ports (Vite proxy and API dev port) to reduce confusion.

## 3) Acceptance Criteria per Milestone

- M1
  - `/panel/` loads; deep links reload correctly (e.g., `/panel/orders/123`).
  - Assets and dynamic chunks load from `/panel/…` without 404s.
- M2
  - `/` loads a functional skeleton with basic navigation.
  - Dev proxy works; no CORS errors.
- M3
  - Nginx history fallback works for both bases; redirect `/admin/*` works with path+query preserved.
- M4
  - CI builds both SPAs; artifacts land in blue/green targets.
  - All smoke probes green pre‑cutover; no backend API changes required.
- M5
  - Staging meets TTFB target and <1% SPA nav errors; UAT signed off.
- M6
  - Production cutover passes smoke; monitoring clean for 30–60 minutes; rollback rehearsed.

## 4) Risks & Mitigations

- SPA 404/missing chunks
  - Use `try_files` fallbacks; ensure hashed assets deployed; monitor 404s.
- Config drift with Caddy
  - Standardize on Nginx; treat Caddy config as deprecated.
- Public POST abuse (leads/orders)
  - Apply Nginx rate limits to `/api/v1/leads` and `/api/v1/orders`.
- Cache busting
  - Rely on content hashes for assets; short TTL for HTML; blue/green minimizes stale clients.
- Blue/green swap logic
  - Verify upstream/roots before switch; run health + SPA loads on target port.

## 5) Performance & Caching Targets

- “/” TTFB < 1s (cached, p90).
- HTML TTL: 5–60 minutes with revalidation.
- Static assets: long TTL (+ `immutable`) with content hashing.
- Optional CDN can mirror headers; no purge needed beyond HTML if hashing used.

## 6) Test Plan

- Smoke (pre/post switch)
  - `GET /api/v1/health` → 200.
  - `GET /panel/` → 200; deep‑link reload.
  - `GET /` → 200; deep‑link reload.
- Navigation error budget
  - <1% SPA navigation/chunk load errors over a 15‑minute window.
- Staging soak
  - Run synthetic checks for 24–48h; validate logs for 404s/missing assets.
- Optional canary
  - If supported, route small % traffic to new env before full cutover.

## 7) Rollout & Backout Playbook

- Rollout
  1. Build Admin (with `VITE_BASE=/panel/`) and Customer SPAs.
  2. Publish dists to non‑active blue/green target.
  3. Apply Nginx config (two SPA blocks, redirect, API proxy) to target env.
  4. Run smoke tests directly against target env port.
  5. Switch Nginx upstream/roots (or symlink `$TARGET`) and reload.
  6. Re‑run smoke via LB; monitor KPIs and logs.
- Backout
  - Revert symlink/upstream to previous env; reload Nginx; re‑run smoke tests.

## 8) Open Questions

- SEO/analytics requirements for “/” (sitemap, CSP allowances, i18n/locale routing)?
- CDN/TLS termination plans (CDN in front of Nginx now or later)?
- Exact rate‑limit thresholds for leads/orders; any IP allowlists?
- Any i18n/branding requirements for the Customer SPA that affect routing or headers?
- Need for cache purge hooks if a CDN is added, or rely solely on content hashing?

*** End of Plan ***

