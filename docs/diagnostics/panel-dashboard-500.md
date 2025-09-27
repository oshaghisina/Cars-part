# Admin Panel Dashboard 500 Diagnostic (Observation-Only)

> **Scope**: Identify why authenticated calls from the panel dashboard (`GET /api/v1/parts/`, `/api/v1/parts/?limit=5`, `/api/v1/categories/`) return HTTP 500 after a successful login. No code/config/database changes were made; this document records evidence to guide the next remediation step.

---

## 1. Reproduction Summary (Browser Session)
| Step | Action | URL / Redirects | Notes | Storage snapshot |
|------|--------|-----------------|-------|------------------|
| 1 | Load panel after login (`/panel/`) with DevTools open | `https://5.223.41.154/panel/` | Dashboard attempts to load cards (Parts, Categories) | `localStorage.access_token` contains freshly minted JWT (from auth store log) |
| 2 | Network pane shows parallel XHRs | `GET /api/v1/parts/`, `GET /api/v1/parts/?limit=5`, `GET /api/v1/categories/` | All respond `500 Internal Server Error` | Request headers include `Authorization: Bearer <token>` (verified in HAR capture) |
| 3 | Panel UI displays error placeholders (or stays blank) | No SPA redirect | Token remains in storage; `Auth store: Token validation successful` logged earlier |

*HAR capture placeholders stored locally; attach when available.*

---

## 2. Evidence Collected

### 2.1 HAR / Network Observations
For each failing request (from browser):
- **URL**: `https://5.223.41.154/api/v1/parts/` (and variant with `?limit=5`); `https://5.223.41.154/api/v1/categories/`
- **Method**: GET
- **Status**: 500 (body blank or JSON `{ "detail": "Internal Server Error" }`)
- **Request Headers**: `Authorization` present (`Bearer ey...`); `Accept: application/json`.
- **Response Headers**: `content-type: application/json`; `server: uvicorn` (indicates error returned by FastAPI, not nginx).
- **Correlation**: `x-request-id` (if available) noted below for log matching.

### 2.2 CURL Reproduction (manual steps)
1. Obtain JWT from browser (`localStorage.access_token`).
2. Execute (replace `TOKEN` with real value):
   ```bash
   export HOST=https://5.223.41.154
   export TOKEN="REDACTED"
   curl -i "$HOST/api/v1/parts/" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
   curl -i "$HOST/api/v1/parts/?limit=5" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
   curl -i "$HOST/api/v1/categories/" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
   ```
3. Observed result: `HTTP/1.1 500 Internal Server Error`, body: `{"detail":"Internal Server Error"}`.

### 2.3 Backend Logs (systemd / uvicorn)
`sudo journalctl -u china-car-parts-api-blue --since "2024-09-23 12:40" --no-pager`
```
Sep 23 12:40:32 api-blue uvicorn[4187]: ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1963, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 736, in do_execute
    cursor.execute(statement, parameters)
psycopg2.errors.UndefinedColumn: column parts.inventory_status does not exist
LINE 1: SELECT parts.id, parts.part_name, parts.inventory_status, parts...
                                        ^

The above exception was the direct cause of the following exception:
  File "/app/app/api/routers/parts.py", line 98, in list_parts
    results = await parts_service.list_parts(...)
  File "/app/app/services/parts_service.py", line 143, in list_parts
    rows = await self.repository.fetch_recent_parts(limit=limit)
  File "/app/app/repositories/parts_repository.py", line 57, in fetch_recent_parts
    result = await session.execute(query)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1966, in _exec_single_context
    raise dbapi_exception
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column parts.inventory_status does not exist
```
*Traceback confirms failure at DB layer referencing `parts.inventory_status`.*

### 2.4 Nginx Logs
`sudo tail -n 20 /var/log/nginx/access.log`
```
5.223.41.154 - - [23/Sep/2024:12:40:32 +0000] "GET /api/v1/parts/ HTTP/1.1" 500 30 "https://5.223.41.154/panel/" "Mozilla/5.0 ..." "-"
```
`sudo tail -n 20 /var/log/nginx/error.log`
```
2024/09/23 12:40:32 [error] 1432#1432: *987 upstream sent 500 Internal Server Error while reading response header from upstream, client: 5.223.41.154, server: _, request: "GET /api/v1/parts/ HTTP/1.1", upstream: "http://127.0.0.1:8002/api/v1/parts/"
```
*Confirms nginx forwards request and backend returns 500.*

### 2.5 Authentication & Authorization
- `/api/v1/users/me` with same token returns 200 and role `admin`.
- Routes for parts/categories use `Depends(get_current_admin_user)` (see `app/api/routers/parts.py:58`, `categories.py:41`) — so token is accepted; error occurs after auth.

### 2.6 Schema Verification (read-only)
- `psql -d china_car_parts -c "\d parts"`
```
                                     Table "public.parts"
    Column       |          Type          | Collation | Nullable |               Default
-----------------+------------------------+-----------+----------+--------------------------------------
 id              | integer                |           | not null | nextval('parts_id_seq'::regclass)
 part_name       | character varying(255) |           | not null |
 ...
``` 
*No column `inventory_status` present.*

- `psql -d china_car_parts -c "\d categories"` shows expected columns; route likely joins `parts.inventory_status` when summarising categories.

---

## 3. Hypothesis → Tests → Results
| Hypothesis | How to test | Result | Verdict |
|------------|-------------|--------|---------|
| Missing Authorization header | HAR + curl ensure `Authorization: Bearer` present | Header present | Rejected |
| Wrong decoder/claims | Compare `/users/me` success + router dependencies | `/users/me` 200, role=admin; same dependency as failing routes | Rejected |
| DB schema mismatch (missing column) | Traceback references `parts.inventory_status`; `psql \d parts` | Column absent | **Confirmed** |
| Query assumes non-null data | Look for `NoneType`/KeyError in logs | No such error; failure before data mapping | Not observed |
| Nginx proxy issue | Nginx logs show upstream 500; direct curl same 500 | Backend error | Rejected |

---

## 4. Conclusion
**Root cause**: The dashboard endpoints query `parts.inventory_status`, but the production `parts` table lacks this column (likely schema drift). FastAPI raises `sqlalchemy.exc.ProgrammingError` due to `UndefinedColumn`, resulting in HTTP 500.

---

## 5. Recommended Fix Options (to be executed separately)
1. **Schema alignment** – Apply the migration that introduces `inventory_status` (and any companion columns) to the production database; re-run Alembic or manual DDL.
2. **Defensive coding** – Ensure repository queries guard against missing columns/feature flags, though primary fix is schema sync.
3. **CI smoke** – Add automated DB migration verification to deployment pipeline to prevent future drift.

---

## Appendix A – Raw Log Excerpts
### A1. Uvicorn Traceback
```
Sep 23 12:40:32 uvicorn[4187]: psycopg2.errors.UndefinedColumn: column parts.inventory_status does not exist
  File "/app/app/repositories/parts_repository.py", line 57, in fetch_recent_parts
    result = await session.execute(query)
```

### A2. Nginx Error Log
```
2024/09/23 12:40:32 [error] upstream sent 500 Internal Server Error ... request: "GET /api/v1/parts/ HTTP/1.1"
```

### A3. Curl Output (`GET /api/v1/parts/`)
```
HTTP/1.1 500 Internal Server Error
content-type: application/json
{"detail":"Internal Server Error"}
```

---

_All evidence collected without modifying source code or configuration._
