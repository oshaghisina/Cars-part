**Executive Summary**

- Public UI serves at `/` (customer-facing SPA). Admin panel serves at `/panel` (admin SPA). API remains stable at `/api/v1/*` behind Nginx.
- Reverse proxy and blue/green deployments run on Nginx. Upstream FastAPI instances listen on `:8001` (active) and `:8002` (standby/next), switched by Nginx config.
- Single-origin strategy for UI + API to avoid CORS issues; dev uses Vite proxy to backend.
- SPA history fallback is enabled so deep links resolve correctly; redirects from `/admin/*` to `/panel/*` maintain backward compatibility.

**Goals**

- Deliver a predictable, same-origin web surface: public at `/`, admin at `/panel`, API at `/api/v1/*`.
- Ensure zero-downtime releases via blue/green swap with health and smoke checks.
- Keep SPA routing robust: history fallback, correct asset bases, and explicit redirect coverage.
- Apply scalable caching: immutable cache for static assets, short TTL for HTML shell, with cache-busting via content hashes.
- Provide clear operational playbooks: health endpoints, rate limits, and straightforward rollback procedures.

**Non-Goals**

- Introducing a second reverse proxy or service mesh layer.
- Migrating to SSR/SSG frameworks or changing SPA framework.
- Rewriting the API surface beyond the stable `/api/v1/*` contract.
- Broad multi-tenant or multi-domain routing beyond the defined origin(s).

**Target Users**

- Customers and leads browsing the public UI at `/`.
- Internal operators/admins using the admin panel at `/panel`.
- DevOps/engineers maintaining the CI/CD and Nginx blue/green deployments.

**Success Metrics**

- Cached TTFB for static assets < 1s at p90 in production (origin + CDN if applicable).
- SPA navigation error rate < 1% (404s/failed chunk loads, route resolution failures).
- `/admin/* → /panel/*` redirect returns 301 and preserves deep paths and query params at p100.
- Blue/green smoke tests pass: `/api/v1/health` 200 via new upstream before switch; final LB health 200 after switch.
- API error rate for public endpoints (search/leads) within error budget; p95 response time < 300ms when cached.

**Constraints & Assumptions**

- Same-origin policy for production/staging: Nginx serves SPA and proxies API to minimize CORS exposure.
- Nginx is the primary ingress/proxy; any legacy Caddy config is deprecated and should not gate traffic.
- Rate limiting applied to public endpoints (login, search, leads) to protect backend resources.
- SPA builds output to `app/frontend/panel/dist` with hashed filenames; HTML shell is short‑cached, assets long‑cached.
- Blue/green toggles by updating Nginx upstream or active server block, not by in-place restarts.
- Dev proxy maps `/api` to FastAPI; local ports are consistent across scripts and Vite proxy settings.

**Acceptance Checklist**

- [ ] Nginx serves public SPA at `/` with `try_files ... /index.html` and cache headers: HTML short TTL, assets immutable.
- [ ] Admin SPA mounted at `/panel` with router base and Vite `base` configured; assets resolve correctly on deep links.
- [ ] `/admin/*` requests 301 to `/panel/*` with path and query preserved.
- [ ] `/api/v1/*` proxied to FastAPI upstream, honoring timeouts and headers; `/api/v1/health` 200.
- [ ] Blue/green flow: new env built, migrations run, health checked on target port, Nginx swap performed, final health verified.
- [ ] Rate limits active on public endpoints (login/search) with appropriate burst settings.
- [ ] Observability: access/error logs enabled, basic performance/health dashboards or scripts available to operators.

**Clarifying Questions**

- Do we require SEO indexing or i18n for the public UI at `/` (sitemap, meta tags, localized routes)? Any noindex needs for staging?
- What analytics/tracking (e.g., GA/GTM) must be included, and are CSP headers defined to allow that?
- Should the public UI include order-tracking flows (e.g., `/orders/:id/status`) that demand unauthenticated read endpoints and cache considerations?
- What default cache policy should Nginx/any CDN apply for HTML vs. assets (TTL, revalidation, immutable)? Any purge hooks needed post-deploy?
- Are there separate staging domains we should codify for allowed origins and health checks (e.g., `staging.example.com`)?

