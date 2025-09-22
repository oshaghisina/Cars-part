# Deployment Spec — Two SPAs + API behind Nginx (Blue/Green)

This spec describes how to serve the Customer SPA at `/`, the Admin SPA at `/panel/`, and the API at `/api/v1/*`, using Nginx with blue/green cutovers.

## 1) Nginx Config (examples)

```nginx
# --- Upstreams (choose active during cutover) ---
# Blue: 8001, Green: 8002
upstream backend_api {
    server 127.0.0.1:8001;  # active (blue)
    # server 127.0.0.1:8002;  # switch to green during cutover
}

# Optional compression (enable if modules available)
gzip on;
gzip_types text/plain text/css application/json application/javascript image/svg+xml;
# brotli on;               # requires ngx_brotli
# brotli_types text/plain text/css application/json application/javascript image/svg+xml;

# Basic security headers (augment per policy)
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header Referrer-Policy strict-origin-when-cross-origin;
# add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;  # TLS only

server {
    listen 443 ssl http2;
    server_name example.com;

    # --- Customer SPA at / ---
    # $TARGET points to active dir (see Blue/Green Layout)
    location / {
        root   $TARGET/app/frontend/web/dist;
        try_files $uri $uri/ /index.html;
    }

    # --- Admin SPA at /panel/ ---
    location /panel/ {
        root   $TARGET/app/frontend/panel/dist;
        try_files $uri $uri/ /panel/index.html;
    }

    # --- API proxy at /api/v1/ ---
    location /api/v1/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # --- Redirect legacy /admin/* → /panel/* ---
    rewrite ^/admin/(.*)$ /panel/$1 permanent;  # preserves querystring
}
```

Notes
- If not using `$TARGET`, set `root` paths to the active blue/green directory explicitly (see next section), or use a stable symlink.
- For HTTP→HTTPS, add a port 80 server that returns 301 to `https://$server_name$request_uri`.

## 2) Blue/Green Layout

Directory structure (example)
```
/opt/china-car-parts-blue/
  app/frontend/web/dist/      # Customer SPA build
  app/frontend/panel/dist/    # Admin SPA build
  venv/                       # Python venv
  .env                        # Environment config
  ... (FastAPI runs on :8001)

/opt/china-car-parts-green/
  app/frontend/web/dist/
  app/frontend/panel/dist/
  venv/
  .env
  ... (FastAPI runs on :8002)

/opt/china-car-parts-active -> /opt/china-car-parts-blue  # symlink to active
```

Switch strategies
- Symlink: Point `/opt/china-car-parts-active` to the target (blue/green), use that path in Nginx `root`, then `nginx -s reload`.
- Environment variable: Export `TARGET` for Nginx (and `env TARGET;` in main config), then reload.

Backout
- Repoint the symlink to the previous environment (or toggle `backend_api` upstream back) and `nginx -s reload`. No rebuild required.

## 3) Cache Strategy

- HTML (index.html): short TTL with revalidation (5–60 minutes). Ensures users pick up new shell after deploy.
- Static assets (hashed filenames): long TTL (e.g., 1 year) with `immutable`.
- Cache-busting: rely on content hashes + blue/green switch; CDN purge is optional.
- If a CDN fronts Nginx, align cache headers and consider a post-deploy purge hook only for HTML if needed.

## 4) CI/CD Pipeline

Build
- Admin SPA: build with `VITE_BASE=/panel/` and router base `/panel/`.
- Customer SPA: build with base `/`.

Publish
- Copy `web/dist` and `panel/dist` to the non-active environment directory (blue or green) under `app/frontend/...`.

Smoke tests (target environment before switch)
- `GET /api/v1/health` returns 200.
- `GET /panel/` returns 200; basic navigation works (deep link reload test: `/panel/orders/123`).
- `GET /` returns 200; basic navigation works (deep link reload test).

Cutover gates
- Cut only if all smoke tests pass. Reload Nginx and verify via LB:
  - `GET /api/v1/health` → 200
  - `GET /panel/` and `GET /` load successfully

Rollback
- Revert symlink/upstream and reload Nginx. Re-run smoke tests on the previous environment.

## 5) Monitoring & Logs

Synthetic checks
- `/` (Customer SPA), `/panel/` (Admin SPA), `/api/v1/health` (backend).

Logs (examples)
- Detect missing chunks/404s:
  - `grep -E "(GET|200|404) /panel/.+(\.js|\.css)" /var/log/nginx/access.log`
  - `grep -E "(404|No such file)" /var/log/nginx/error.log`
- Track SPA navigation errors via client telemetry (if available) and alert if >1% over 5–15 minutes.

Error budget
- SPA navigation error rate < 1% (rolling window).

## 6) Security & Rate Limits

Nginx examples
```nginx
# Define zones in http {}
limit_req_zone $binary_remote_addr zone=leads:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=orders:10m rate=5r/m;

# Apply to specific endpoints
location ~ ^/api/v1/leads/?$ {
    limit_req zone=leads burst=10 nodelay;
    proxy_pass http://backend_api;
}

location ~ ^/api/v1/orders/?$ {
    limit_req zone=orders burst=10 nodelay;
    proxy_pass http://backend_api;
}
```

Notes
- Admin auth model (JWT) remains unchanged; same-origin cookies permitted.
- Tune rates based on production traffic; start conservative in staging.

## 7) Staging vs Production

- Caching: shorter HTML TTL in staging (e.g., 5–10 minutes); production up to 60 minutes.
- Logging: higher verbosity in staging; production focuses on errors and key metrics.
- Smoke coverage: staging includes deep-link route coverage for both SPAs; production cutover runs a minimal but representative set.
- Robots: staging responds with `Disallow: /`; production allows indexing if applicable.

## 8) Acceptance Checklist

- [ ] Nginx blocks validated: `/`, `/panel/`, and `/api/v1/` work with correct fallbacks.
- [ ] Both SPAs load with deep links and hashed assets resolve.
- [ ] API unaffected; `/api/v1/health` passes pre/post switch.
- [ ] Redirect `/admin/* → /panel/*` verified (path + query preserved).
- [ ] Smoke tests green pre-cutover and post-cutover.
- [ ] Rollback path validated (symlink/upstream revert restores service).

## 9) Open Questions

- Is a CDN/Cloudflare in front of Nginx? Where is TLS terminated?
- Exact TTL values and headers to standardize (HTML vs assets)?
- SEO/analytics requirements for `/` (sitemap, CSP allowances, i18n)?
- Rate-limit thresholds for leads/orders in production?
- Any need for cache purge hooks or will hash-based busting suffice?

