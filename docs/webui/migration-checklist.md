# Migration Checklist — Move Admin SPA from / to /panel

Concise, implementation-agnostic checklist to migrate the existing Admin SPA from the root path (`/`) to `/panel`, keep the API at `/api/v1/*`, and prepare the root (`/`) for a future public web SPA.

## 1) Frontend (Admin SPA)

- [ ] Router base → use `createWebHistory('/panel/')`
- [ ] Vite base → `base: process.env.VITE_BASE || '/'` and set `VITE_BASE=/panel/` for production builds
- [ ] Asset paths → verify CSS/IMG/Fonts resolve under `/panel/`
- [ ] Local dev note → base stays `/` for dev unless otherwise configured
- [ ] Deep-link test → reload on a nested route (e.g., `/panel/orders/123`) loads index and route correctly
- [ ] Chunk paths → confirm dynamic imports/chunks load from `/panel/assets/*`
- [ ] QA checklist → navigation, auth redirect, and 404 page all work from `/panel` base

## 2) Backend/Proxy (Nginx)

- [ ] Serve Admin SPA at `/panel/` from the admin build output directory
- [ ] Reserve root (`/`) for the public web SPA (or placeholder) with history fallback
- [ ] Keep API proxy at `/api/v1/` unchanged (timeouts, headers, upstream)
- [ ] Add permanent redirect `/admin/* → /panel/*` (preserve path and query)
- [ ] Cache policy → short TTL for HTML, long-lived immutable for assets
- [ ] Blue/green → ensure both environments have updated config before switching

```nginx
# Admin SPA at /panel/
location /panel/ {
  root   $TARGET/app/frontend/panel/dist;
  try_files $uri $uri/ /panel/index.html;
}

# Public web SPA at /
location / {
  root   $TARGET/app/frontend/web/dist;
  try_files $uri $uri/ /index.html;
}

# API proxy stays unchanged
location /api/v1/ {
  proxy_pass http://backend_upstream;
}

# Redirect legacy /admin/* → /panel/*
rewrite ^/admin/(.*)$ /panel/$1 permanent;
```

