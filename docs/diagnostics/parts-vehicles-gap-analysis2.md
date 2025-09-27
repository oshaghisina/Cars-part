# Parts & Vehicles Data Connectivity – Gap Analysis (Iteration 2)

## Executive Summary
Buyer- and vendor-facing flows depend on the `/api/v1/parts` resources, yet pricing, stock, and vendor context are absent across the database, API responses, and front-end integrations. The public storefront therefore fabricates prices and availability, while the admin panel submits payloads that the backend rejects. Until schema, API, and UI contract are aligned, buyers cannot reliably select real inventory and vendors cannot manage it.

## Current State Overview

### Database
- Inspected `sqlite:///./data/app.db` tables relevant to parts, pricing, vehicles, leads, and orders.
- `parts` table lacks ownership/stock columns (`vendor_id`, `current_stock`, `reserved_quantity`, `price`) – schema showed only descriptive fields and timestamps.
- Inventory-like data is partially stored in `prices` (per-seller price, available_qty) and `stock_alerts` (customer notifications), but neither references a vendor user.
- Vehicle reference tables (`vehicle_brands`, `vehicle_models`, `vehicle_trims`) exist with expected descriptive columns.

### API
- `GET /api/v1/parts/` returns 200 with `X-Total-Count`, but payload omits price/stock fields (`sample_body` shows only descriptive metadata).
- `GET /api/v1/categories/` succeeds; `GET /api/v1/vehicles/brands` works, but `GET /api/v1/vehicles/` (without segment) is a 404 (no index route).
- `GET /api/v1/parts/{id}` succeeds for existing IDs, though inactive parts remain accessible; PDP endpoint (`/api/v1/pdp/parts/{id}`) returns `prices: null`, `in_stock: false` for active records.
- Authentication with documented defaults (`admin` / `adminpassword`) fails (401). Without a valid token, vendor POST/PATCH flows cannot be exercised.
- Simulated panel payload (`name`, `price`, `stock_quantity`, …) against `POST /api/v1/parts/` yields 422 because the backend expects `part_name`, `brand_oem`, `vehicle_make`, etc. No `PATCH` handler exists (`405 Method Not Allowed`).

### Frontend
- **Admin Panel (`PartForm.vue`)** collects `name`, `price`, `stock_quantity`, `minimum_stock`, boolean flags, and sends the raw form object to the store. These fields do not line up with the backend’s schema, so create/update calls default to 422 errors.
- **Customer Web (`Search.vue`)** relies on `/api/v1/parts/` but, because responses lack price/stock, it calls `generatePrice()` and `generateStock()` helpers to fabricate values client-side. PDP (`BuyBox.vue`) expects `part.price`, `part.stock`, `part.proPrice`, yet the API supplies none, leaving critical UI states dependent on mock data.

## Evidence
- `PRAGMA table_info(parts);` → columns stop at `updated_at`, confirming no price/stock/vendor fields (`app/db/models.py` aligns with this schema).
- `GET /api/v1/parts/` via TestClient → 200, header `x-total-count: 15`, body sample lacks price/stock fields (`Diagnostic script`, TestClient output).
- `GET /api/v1/pdp/parts/14` → 200 with `prices: null`, `best_price: null`, `in_stock: false` (active PDP record).
- `POST /api/v1/users/login` (`admin` / `adminpassword`) → 401 `Invalid username/email or password`.
- `POST /api/v1/parts/` with panel-style payload (`name`, `price`, `stock_quantity`, …) → 422 missing `part_name`, `brand_oem`, etc.
- `PATCH /api/v1/parts/1` → 405 Method Not Allowed.
- `PartForm.vue` (lines 205–265) binds `formData.price`, `stock_quantity`, `minimum_stock`, demonstrating UI expectation for inventory fields absent in API/DB.
- `Search.vue` (lines 604–660) defines `generatePrice()` and `generateStock()` mock functions, highlighting lack of real pricing/inventory data from the API.

## Gap Analysis

| Gap | Evidence | Impact | Severity |
| --- | --- | --- | --- |
| Parts table lacks vendor ownership and inventory columns (`vendor_id`, `current_stock`, `price`). | `PRAGMA table_info(parts);` output; `app/db/models.py` definition. | Cannot attribute inventory to vendors or record stock/price; downstream services have no authoritative inventory source. | **High** |
| Admin panel payload schema mismatched with API contract (expects `name`, `price`, `stock_quantity`). | `PartForm.vue` (fields) vs. 422 response when posting payload to `/api/v1/parts/`. | Vendor UI actions fail with validation errors; no path to create/update parts. | **High** |
| Public site relies on mock pricing/stock due to API omissions. | `Search.vue` `generatePrice`/`generateStock`; PDP response with `prices: null`. | Buyers see fabricated prices/availability; selection flow cannot surface real stock. | **High** |
| PDP endpoint returns `prices: null` / `in_stock: false` even for active parts. | `/api/v1/pdp/parts/14` response. | Detailed product view lacks price and stock, blocking checkout readiness and confusing buyers. | **High** |
| No authenticated vendor/admin login available for API testing (default credentials invalid). | `POST /api/v1/users/login` 401. | Vendor scenario cannot be validated; automation and documentation rely on unknown credentials. | **Medium** |
| Vehicle API lacks index route (`GET /api/v1/vehicles/` → 404). | TestClient GET result. | Minor UX/API inconsistency; requires clients to know subpaths. | **Low** |

## Recommendations & Next Steps
1. **Unify data model for inventory management**
   - Extend `parts` (or introduce `part_inventory`) with `vendor_id` (FK to `users`), `current_stock`, `reserved_quantity`, `backorder_eta`, `base_price`.
   - Normalize vendor-price relationships: either link `prices.seller_name` to a vendor record or consolidate pricing into the inventory table.

2. **Align API contracts with panel and web requirements**
   - Update `PartCreateRequest`/`PartUpdateRequest` to accept `name`/`price`/`stock` fields or adjust panel payload mapping before submission.
   - Implement stock/price update endpoints (`PUT/PATCH /api/v1/parts/{id}` or `/api/v1/parts/{id}/inventory`) returning updated values.
   - Return pricing collections (or at least `best_price`, `inventory_status`) from `/api/v1/parts/` and `/api/v1/pdp/parts/{id}`.

3. **Restore real pricing and inventory to the storefront**
   - Replace `generatePrice()` / `generateStock()` with real data from the updated API.
   - Ensure PDP `BuyBox` props map to backend fields (e.g., `part.best_price`, `part.in_stock`, `part.available_qty`).

4. **Vendor authentication & role clarity**
   - Document working admin/vendor credentials for staging or provide seeded vendor accounts with known passwords.
   - Enforce role-based access in the API (e.g., vendor can mutate only owned parts once `vendor_id` exists).

5. **Acceptance criteria to validate readiness**
   - Buyer journey: `/api/v1/parts` and `/api/v1/pdp/parts/{id}` return price + stock; storefront renders same values; checkout receives valid inventory references.
   - Vendor journey: Admin panel form submission creates/updates parts without validation errors; stock changes reflected in API responses within one round-trip.

6. **Minor API hygiene**
   - Add a discovery endpoint for `/api/v1/vehicles/` (e.g., redirect to `/brands`) to reduce 404 confusion for clients.

By addressing these gaps in order—schema, API contracts, then UI wiring—both customer-facing discovery and vendor inventory workflows can operate against consistent, reliable data.
