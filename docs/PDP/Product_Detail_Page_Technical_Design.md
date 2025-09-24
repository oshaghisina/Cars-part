# Product Detail Page (PDP) — Technical Design

Status: Approved functional spec (Stage 1); this document defines the implementation plan.
Owner: Web Team (Vue.js/Nuxt.js) + API Team (FastAPI)

## 1) API Contract

Scope covers PDP data aggregation and supporting flows: product detail, compatibility, alternatives, installer slots, and cart. All endpoints are versioned and live under `/api/v1`. Responses are JSON. Unless specified, requests are unauthenticated (retail). Pro users must include `Authorization: Bearer <JWT>` with a `role=pro` claim.

### 1.1 Product Detail (Aggregator)
- Method: GET
- Path: `/api/v1/products/{idOrSlug}`
- Query params:
  - `vehicleId` (optional, string) — selected vehicle/trim to personalize fitment and availability
  - `include` (optional, CSV; default: `price,availability,media,fitment,specs,related,warranty,policies`) — allow trimming response
- Roles:
  - Retail: receives consumer price fields; no tier/bulk pricing
  - Pro: receives tier pricing, MOQ, net price; marked as `proOnly`
- Response: 200 JSON, 404 when not found
- Error codes: 400 invalid params; 503 downstream failure
- Response schema (simplified):
```json
{
  "product": {
    "id": "12345",
    "slug": "oil-filter-sqrf4j16",
    "sku": "OF-123",
    "name": "Oil Filter",
    "brand": "OEM",
    "category": {"id": "cat-12", "name": "Filters"},
    "media": [
      {"type": "image", "url": "https://.../main.jpg", "alt": "Oil filter", "width": 1200, "height": 1200}
    ],
    "price": {
      "currency": "IRR",
      "list": 1250000,
      "sale": 1090000,
      "savingsPct": 12.8,
      "proNet": 980000,            
      "moq": 10,                  
      "tiers": [                  
        {"minQty": 10, "price": 980000},
        {"minQty": 50, "price": 940000}
      ]
    },
    "availability": {
      "stockStatus": "in_stock",
      "availableQty": 42,
      "leadTimeDays": 2,
      "warehouses": [{"code": "THR", "qty": 30}, {"code": "SHZ", "qty": 12}]
    },
    "fitment": {
      "vehicleId": "trim-8893",
      "isCompatible": true,
      "coverage": {"years": [2018, 2019, 2020], "engineCodes": ["SQRF4J16"]},
      "notes": ["Verify VIN for 2021+ models"]
    },
    "oemRefs": [
      {"brand": "Chery", "oemCode": "S11-1012010", "note": null}
    ],
    "crossRefs": [
      {"brand": "Hengst", "code": "E123H", "type": "equivalent", "confidence": 0.93}
    ],
    "specs": [
      {"name": "Thread", "value": "M20x1.5"},
      {"name": "Height", "value": "120", "unit": "mm"}
    ],
    "reviews": {
      "count": 12,
      "average": 4.3,
      "ratingDist": {"1": 0, "2": 1, "3": 2, "4": 4, "5": 5},
      "items": [
        {"id": "r-1", "rating": 5, "title": "Works great", "body": "...", "createdAt": "2024-04-11"}
      ]
    },
    "kit": {"items": [{"productId": "6789", "qty": 1}]},
    "related": [{"productId": "4321", "relationship": "also_bought"}],
    "warranty": {"type": "limited", "periodMonths": 12},
    "policies": {"shipping": {"minDays": 2, "maxDays": 5}, "returns": {"days": 7}}
  },
  "flags": {"requiresInstaller": false, "hazmat": false}
}
```
- Notes:
  - For retail users, `price.proNet`, `price.moq`, and `price.tiers` MUST be omitted.
  - For pro users, SSR responses must not be cached publicly (see Caching/ISR).

### 1.2 Compatibility Check
- Method: GET
- Path: `/api/v1/products/{idOrSlug}/compatibility`
- Query params: `vehicleId` (required), `vin` (optional)
- Roles: Same response for retail and pro
- Response 200:
```json
{
  "productId": "12345",
  "vehicleId": "trim-8893",
  "isCompatible": true,
  "coverage": {"years": [2018, 2019, 2020], "engineCodes": ["SQRF4J16"]},
  "notes": []
}
```
- Errors: 400 (missing vehicleId), 404 (product not found)

### 1.3 Alternatives / Cross-sell
- Method: GET
- Path: `/api/v1/products/{idOrSlug}/alternatives`
- Query params:
  - `type` = `equivalents|upgrades|downgrades|kits|related` (default: `equivalents`)
  - `limit` (default 10)
- Response 200:
```json
{
  "productId": "12345",
  "type": "equivalents",
  "items": [
    {"productId": "9876", "score": 0.92, "reason": "OEM cross-ref"}
  ]
}
```

### 1.4 Installer Slots (Feature-flagged)
- Method: GET
- Path: `/api/v1/installer/slots`
- Query params: `postalCode` (required), `date` (ISO date, optional), `radiusKm` (default 25)
- Response 200:
```json
{
  "postalCode": "11369",
  "date": "2025-04-02",
  "vendors": [
    {
      "id": "v-12",
      "name": "QuickFit Garage",
      "slots": [
        {"from": "09:00", "to": "10:00"},
        {"from": "10:00", "to": "11:00"}
      ]
    }
  ]
}
```
- Errors: 503 if external provider unavailable

### 1.5 Cart
- Resource base: `/api/v1/cart` (session-based; cookie `cartId` or header `X-Cart-Id`)
- Security: Retail or Pro allowed; Pro may see net/tier prices in-line calculations

1) Get cart
- Method: GET `/api/v1/cart`
- Response 200:
```json
{
  "id": "c_abc123",
  "currency": "IRR",
  "items": [
    {
      "itemId": "i_1",
      "productId": "12345",
      "sku": "OF-123",
      "name": "Oil Filter",
      "qty": 2,
      "unitPrice": 1090000,
      "lineTotal": 2180000,
      "meta": {"vehicleId": "trim-8893"}
    }
  ],
  "subtotal": 2180000,
  "discounts": [],
  "total": 2180000
}
```

2) Add item
- Method: POST `/api/v1/cart/items`
- Body:
```json
{"productId": "12345", "qty": 2, "vehicleId": "trim-8893"}
```
- Response 201: cart payload (as above)
- Errors: 409 if insufficient stock; 422 validation

3) Update item
- Method: PATCH `/api/v1/cart/items/{itemId}`
- Body:
```json
{"qty": 3}
```
- Response 200: cart payload

4) Remove item
- Method: DELETE `/api/v1/cart/items/{itemId}`
- Response 204

### 1.6 Price for Pro (Optional granular endpoint)
- Method: GET `/api/v1/products/{idOrSlug}/price`
- Query: `qty` (optional)
- Role: Pro only (403 otherwise)
- Response 200:
```json
{"currency": "IRR", "net": 980000, "moq": 10, "tiers": [{"minQty": 10, "price": 980000}]}
```

### 1.7 Standard Error Payload
All new endpoints return structured errors with consistent envelope.
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Product not found",
    "status": 404,
    "requestId": "req_7fQ...",
    "details": {"idOrSlug": "abc"}
  }
}
```
Mapping:
- 400 INVALID_REQUEST
- 401 UNAUTHENTICATED
- 403 FORBIDDEN
- 404 RESOURCE_NOT_FOUND
- 409 CONFLICT
- 422 UNPROCESSABLE_ENTITY
- 429 RATE_LIMITED
- 500 INTERNAL_ERROR
- 503 SERVICE_UNAVAILABLE


## 2) Data Models (TypeScript)
The following interfaces describe response shapes used by the PDP.

```ts
// Common
export type Currency = "IRR" | "USD" | "EUR";
export type StockStatus = "in_stock" | "low_stock" | "backorder" | "pre_order" | "discontinued";
export type AltType = "equivalent" | "upgrade" | "downgrade" | "kit" | "related";

export interface Media {
  type: "image" | "video" | "pdf";
  url: string;
  alt?: string;
  width?: number;
  height?: number;
  thumbnailUrl?: string;
  blurHash?: string;
}

export interface PriceTier { minQty: number; price: number; }

export interface Price {
  currency: Currency;
  list?: number;         // retail list price
  sale?: number;         // retail discounted price
  savingsPct?: number;   // convenience field
  proNet?: number;       // pro-only
  moq?: number;          // pro-only
  tiers?: PriceTier[];   // pro-only
}

export interface Availability {
  stockStatus: StockStatus;
  availableQty?: number;
  leadTimeDays?: number;
  warehouses?: { code: string; qty?: number }[];
}

export interface Fitment {
  vehicleId?: string;        // selected trim/vehicle
  isCompatible: boolean;
  coverage?: {
    years?: number[];
    engineCodes?: string[];
    notes?: string[];
  };
  notes?: string[];
}

export interface OEMRef { brand: string; oemCode: string; note?: string | null; }
export interface CrossRef { brand: string; code: string; type: AltType | "equivalent"; confidence?: number; }

export interface Spec { name: string; value: string; unit?: string; type?: "text" | "number" | "boolean" | "enum"; }

export interface ReviewItem {
  id: string;
  rating: 1 | 2 | 3 | 4 | 5;
  title?: string;
  body: string;
  createdAt: string; // ISO
  author?: { id?: string; name?: string };
  attachments?: Media[];
}

export interface Reviews {
  count: number;
  average: number; // 0..5
  ratingDist?: Record<string, number>;
  items?: ReviewItem[];
}

export interface KitItem { productId: string; qty: number; }
export interface Kit { items: KitItem[]; note?: string; }

export interface RelatedItem { productId: string; relationship: "also_bought" | "similar" | "accessory" | "replacement"; }

export interface Warranty { type: "none" | "limited" | "lifetime"; periodMonths?: number; detailsUrl?: string; }

export interface Policies {
  shipping?: { minDays?: number; maxDays?: number; method?: string };
  returns?: { days?: number; restockingFeePct?: number };
  termsUrl?: string;
}

export interface Product {
  id: string;
  slug: string;
  sku: string;
  name: string;
  brand: string;
  category?: { id: string; name: string };
  subcategory?: { id?: string; name?: string };
  media?: Media[];
  price?: Price;
  availability?: Availability;
  fitment?: Fitment;
  oemRefs?: OEMRef[];
  crossRefs?: CrossRef[];
  specs?: Spec[];
  reviews?: Reviews;
  kit?: Kit | null;
  related?: RelatedItem[];
  warranty?: Warranty;
  policies?: Policies;
  flags?: Record<string, boolean>;
}

// Cart
export interface CartItem {
  itemId: string;
  productId: string;
  sku: string;
  name: string;
  qty: number;
  unitPrice: number;
  lineTotal: number;
  meta?: { vehicleId?: string };
}

export interface Cart {
  id: string;
  currency: Currency;
  items: CartItem[];
  subtotal: number;
  discounts?: { code: string; amount: number }[];
  total: number;
}
```

Optionally, Zod schemas may be co-located in `src/types/pdp.ts` to validate runtime responses during SSR.


## 3) Frontend Architecture (Vue.js 3 + Nuxt.js)

- Rendering strategy
  - Use Nuxt.js SSR for the PDP route to deliver SEO-friendly content and fast LCP.
  - Hydrate interactivity blocks (gallery, fitment selector, reviews, installer widget) as Client Components.
  - Parallel data fetching on the server: product, alternatives, reviews (feature-flagged).

- Suggested file structure
```
app/frontend/web/
  pages/
    products/
      [slug].vue              // SSR: fetch product by slug
  components/
    pdp/
      Gallery.vue             // Client
      PriceBlock.vue          // Client (handles tier price toggle for pro)
      Availability.vue        // Client (subscribe to stock updates)
      FitmentSelector.vue     // Client (reads saved vehicle)
      OEMCrossRefs.vue        // Client
      Specs.vue               // Client
      Reviews.vue             // Client (feature-flagged)
      RelatedProducts.vue     // Client w/ lazy load
      KitBundle.vue           // Client
      InstallerWidget.vue     // Client (feature-flagged)
      AddToCartButton.vue     // Client
  composables/
    useProduct.ts             // product data fetching and state
    useCart.ts                // cart management
    useFitment.ts             // vehicle compatibility
    useFeatureFlags.ts        // feature flag management
  utils/
    api/
      client.ts               // fetch wrapper with base URL, auth, caching
      products.ts             // typed fetchers
      cart.ts
      installer.ts
    analytics/
      events.ts               // event names + payload types
      track.ts                // transport (sendBeacon/fetch)
    cookies.ts                // helpers for saved vehicle
  types/
    pdp.ts                    // interfaces above
  plugins/
    featureFlags.client.ts    // client-side feature flag initialization
```

- State management
  - Primary data is server-fetched per request using Nuxt's `useFetch` or `$fetch`.
  - Saved vehicle persists in `localStorage` and `cookie` (`savedVehicleId`) for SSR awareness.
  - Fitment selector reads localStorage, posts selection to API endpoint to set the cookie, and refreshes the PDP via router.

- Feature flags
  - Build-time: `NUXT_PUBLIC_FEATURE_INSTALLER_WIDGET`, `NUXT_PUBLIC_FEATURE_REVIEWS`.
  - Runtime: allow server to inject `x-feature-*` headers or a `/api/v1/flags` public endpoint to override.
  - `useFeatureFlags.ts` composable merges env + runtime flags; components check flags to render or no-op.

- Vue.js specific implementation notes
  - Use `<script setup>` syntax for all components for better TypeScript support.
  - Implement reactive state management using Vue 3 Composition API with `ref()`, `reactive()`, and `computed()`.
  - Use `defineProps()` and `defineEmits()` for component communication.
  - Leverage Nuxt's auto-imports for `useFetch`, `useRoute`, `useRouter`, `useHead`, etc.
  - Implement proper TypeScript support with `defineComponent` and proper typing for props/emits.
  - Use Nuxt's built-in SEO features with `useSeoMeta()` and `useHead()` for dynamic meta tags.
  - Implement proper error boundaries using Nuxt's error handling system.


## 4) Error Handling (Frontend Behavior)

- 404 (product not found)
  - Use Nuxt.js `throw createError({ statusCode: 404 })` → `error.vue` with search redirect and "browse category" CTA.

- 503 (service unavailable/timeouts)
  - Render `error.vue` with retry button, show partial blocks if any data resolved.
  - Defer non-critical blocks (reviews, related) and show skeleton placeholders.

- Empty states / missing data
  - Media: show generic product placeholder image; keep gallery skeleton sizes for layout stability.
  - Specs: render "Specifications not available" message and link to contact.
  - Fitment unknown: default to "Check compatibility" prompt and disable Add-to-Cart until confirmed if part requires strict fitment.


## 5) Integration Notes

- Required environment variables
  - `NUXT_PUBLIC_SITE_NAME`
  - `NUXT_PUBLIC_API_BASE_URL` (e.g., `https://api.company.com`)
  - `NUXT_PUBLIC_FEATURE_INSTALLER_WIDGET` ("0" | "1")
  - `NUXT_PUBLIC_FEATURE_REVIEWS` ("0" | "1")
  - `JWT_PUBLIC_KEY` or backend-configured `Authorization` bearer token provider

- Auth and role detection
  - Pro users authenticate; JWT includes `role=pro` claim (aligned with FastAPI `app/core/auth.py`).
  - Client sends `Authorization: Bearer <JWT>`; server SSR fetch uses the same token via cookies/headers.
  - Backend guards pro-only endpoints/fields; redact pro pricing in retail responses.

- Caching / ISR
  - Retail PDP: `revalidate: 300` (5 minutes) for product payload; tag-based revalidation when prices change.
  - Pro views: fetch with `cache: "no-store"` or `Cache-Control: private` and skip ISR to avoid leaking personalized pricing.
  - Fragment-level caching for alternatives and reviews with longer TTL (e.g., 30 minutes).

- Performance targets
  - SSR LCP < 2s on 4G; TTFB < 500ms p75.
  - Image optimization via Nuxt Image and CDN; serve WebP/AVIF with responsive sizes.
  - Lazy-load heavy blocks: reviews, related products, installer widget.
  - Minimize JS on initial route; keep gallery and price blocks small.


## 6) Security & Access Control

- Pro data handling
  - Never include `proNet`, `moq`, `tiers` in retail responses.
  - Use role-based guards server-side; add schema-level redaction before serialization.
  - Ensure pro SSR responses are not cached publicly; set `Vary: Authorization, X-User-Role`.

- Prevent bulk pricing leakage
  - Cart recomputation must respect role from token per request.
  - Do not echo pricing rules in client; compute on server.

- Input validation and rate limiting
  - Validate `vehicleId`, `qty` ranges; limit cart mutations (429) to mitigate abuse.
  - Optional `X-Idempotency-Key` on cart POST to avoid duplicate adds.

- PII & logs
  - Avoid logging full JWTs; include `requestId` in structured logs.


## 7) Testing Plan

- Unit tests (Vitest + Vue Test Utils)
  - Components: `PriceBlock`, `FitmentSelector`, `AddToCartButton` behaviors and edge cases.
  - Composables: `useFeatureFlags.ts`, `utils/api/client.ts` error handling and retries.

- API mocking (MSW)
  - Handlers for: product detail, compatibility, alternatives, cart, installer slots.
  - Retail vs Pro variants to verify conditional rendering and redaction.

- Integration tests (Playwright or Vue Test Utils + Nuxt Test)
  - PDP load → shows name, price, gallery skeleton → renders images.
  - Change fitment (vehicle) → compatibility indicator updates, Add-to-Cart enabled/disabled.
  - Add to cart → cart badge updates; server errors (409/503) show inline toasts.

- Analytics acceptance
  - Fire `pdp_view` with `{ productId, sku, category, role, source }` on SSR hydration.
  - `add_to_cart` includes `{ productId, qty, price, role, vehicleId }`.
  - Use `@vue/test-utils` + MSW to assert beacon payloads; provide fallback to fetch when `sendBeacon` not available.


---

### Backend Implementation Notes (FastAPI alignment)
- Add a `products` router under `/api/v1/products` that aggregates from existing models: `Part`, `Price`, `PartImage`, `PartSpecification` in `app/db/models.py`.
- Compatibility can be derived from `Part.vehicle_*` fields initially; future: join with `Vehicle*` models.
- Pro role detection reuses `require_role("pro")` (extend role mapping to include `pro`).
- Standardize error envelope via FastAPI exception handlers.

### Migration & Rollout
- Phase 1: Implement aggregator read-only endpoints and retail PDP in Vue.js/Nuxt.js.
- Phase 2: Add Pro pricing and Cart endpoints; enforce private caching for pro.
- Phase 3: Enable Installer widget and Reviews behind feature flags.
