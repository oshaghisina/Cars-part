## Product Detail Page (PDP) — UX Specification (Stage-1 Aligned)

Status: UX Spec v1.0 (aligns with approved Functional Spec)
Owner: UX Team • Stakeholders: Web (Vue/Nuxt), API (FastAPI), PM

### 1) UX Principles & Constraints

- **Compatibility-first**: The interface prioritizes confirming vehicle fit before purchase. The Fitment Bar is prominent, sticky on mobile, and updates all downstream blocks.
- **Clarity**: Progressive disclosure; show essential info first (title, price, stock, compatibility), with expandable details (specs, refs, reviews).
- **Trust**: Authorized brand badges, warranty/returns surfacing, verified-purchase indicators, OEM/cross-reference transparency.
- **Mobile-first**: Layout designed for mobile core flows; desktop enhances with multi-column views. Sticky primary CTA on mobile.
- **Accessibility**: WCAG 2.1 AA targets; keyboard-first navigation, ARIA roles, live regions for dynamic states.
- **Performance**: Support Core Web Vitals (fast LCP via SSR-rendered title/price/media, defer non-critical blocks, lazy-load below-the-fold).

Constraints
- API (Stage-2) provides: product, fitment status, alternatives, installer slots, cart.
- Role-aware pricing (retail vs pro) must never leak pro-only fields to retail.
- Network resilience: graceful fallbacks for media and partial data.

---

### 2) Page Blueprint (Desktop & Mobile)

Legend: [C] Critical • [H] High • [M] Medium • [L] Low

Desktop (2-column above the fold; 1-column below)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Breadcrumbs / Category                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Fitment Bar [C] (VIN | Plate | Manual)  [Saved Vehicle Chip]  Status pill   │
├──────────────────────────────────────────────────────────────────────────────┤
│  Media Gallery [H]         │  Title Block [C]                                │
│  - zoom/360/video          │  - brand, name, SKU/MPN/OEM/EAN                 │
│                            │  - badges (authentic, best-seller)              │
│                            │  Buy Box [C]                                    │
│                            │  - price (retail/pro), stock, ETA, qty, CTAs    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Installer Widget [M]  | Cross-Reference & Supersession [H] | Specs & Notes   │
├──────────────────────────────────────────────────────────────────────────────┤
│ Kits & Bundles [M]  | FAQ/How-to [M] | Reviews [H] | Related/Alternatives [H]│
├──────────────────────────────────────────────────────────────────────────────┤
│ Policies & Trust [H] (warranty, returns, authenticity)                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

Mobile (single column with sticky CTA)

```
┌──────────────────────────────────────┐
│ Breadcrumbs                          │
├──────────────────────────────────────┤
│ Fitment Bar [C] (sticky at top)      │
├──────────────────────────────────────┤
│ Media Gallery [H] (swipe, zoom)      │
├──────────────────────────────────────┤
│ Title Block [C]                      │
│ Buy Box [C] (sticky CTA at bottom)   │
├──────────────────────────────────────┤
│ Installer (opt) • Cross-Refs • Specs │
│ Kits • FAQ • Reviews • Related       │
├──────────────────────────────────────┤
│ Policies & Trust                     │
└──────────────────────────────────────┘
```

Block details (purpose, inputs/outputs, states, empty/error/loading):

A) Fitment Bar
- Purpose: Resolve compatibility early; persist vehicle context.
- Inputs: VIN/Plate fields; Manual selector (Year/Make/Model/Engine/Trim); saved vehicle chip; API fitment.
- Outputs: `fitmentStatus` (compatible | incompatible | requires_verification | unknown), selected `vehicleId`.
- States: idle, validating, compatible, incompatible, requires_verification, unknown, API error, offline.
- Loading: inline spinner; disable CTAs that require compatibility (if strict fitment).
- Empty: collapsed form with prompt “Check if this fits your vehicle”.
- Errors: toast + inline field error; preserve user input.

B) Title Block
- Purpose: Establish identity/trust.
- Inputs: brand, part name, SKU/MPN/OEM/EAN, badges (authorized, best-seller, OEM, new).
- Outputs: semantic title, structured IDs (for copy/download), badge list.
- States: normal; missing IDs show “—”.
- Loading: skeleton lines.
- Empty/Error: fall back to SKU when name missing; show brand placeholder.

C) Media Gallery
- Purpose: Visual inspection; reduce uncertainty.
- Inputs: images (angles), 360 asset, videos; alt text.
- Outputs: current media, zoom state, modal state.
- States: image present, 360 present, video present; missing media; error loading.
- Loading: image skeletons with preserved aspect; defer heavy assets.
- Empty/Error: generic product placeholder; hide 360/video tabs if unavailable.

D) Buy Box
- Purpose: Conversion controls.
- Inputs: price (retail/pro), stock status, availableQty, ETA (by city), qty, role, fitmentStatus.
- Outputs: actions (Add to Cart, Buy Now, Add to Quote for pro), messaging (stock/ETA/fitment).
- States: stock (in_stock | low_stock | out_of_stock | discontinued | backorder | pre_order), role (retail/pro), fitment states.
- Loading: price/stock skeletons, disabled CTAs.
- Empty/Error: price unavailable → “Contact support”; stock error → “Check availability”.

E) Installer Widget (optional)
- Purpose: Book installation near user.
- Inputs: city/postalCode, date, slots API.
- Outputs: selected vendor+slot; deep link to booking/confirmation.
- States: feature-flag off; no vendors; slots loaded; error/timeout.
- Loading: slot skeleton, retry.
- Empty/Error: suggest self-install guide.

F) Cross-Reference & Supersession
- Purpose: Verify authenticity and alternatives.
- Inputs: OEM refs, cross refs (equivalent/upgrade/downgrade), supersession notes.
- Outputs: list with copy-to-clipboard; link outs.
- States: present/empty/error.
- Loading: table skeleton.
- Empty/Error: “No references available.”

G) Specs & Notes
- Purpose: Technical validation and caveats.
- Inputs: specs (key/value/unit), notes, compatibility notes.
- Outputs: expandable groups, searchable table.
- States: present/empty/error.
- Loading: table skeleton.
- Empty: “Specifications not available.”

H) Kits & Bundles
- Purpose: Increase AOV; ensure completeness.
- Inputs: kit items (productId, qty), availability.
- Outputs: add-kit CTA; per-item add.
- States: present/empty/error; OOS kit items.
- Loading: cards skeleton.

I) FAQ / How-to
- Purpose: Reduce support load; educate.
- Inputs: curated FAQs, how-to links/videos.
- Outputs: accordion; deep link to Help Center.
- States: present/empty.

J) Reviews
- Purpose: Social proof.
- Inputs: summary (avg, count, dist), items, verified purchase.
- Outputs: filters (rating, verified), sort, pagination.
- States: present/empty/moderated; posting/auth required.
- Loading: list skeleton.

K) Related / Alternatives
- Purpose: Recovery and discovery.
- Inputs: alternatives reason (OOS/incompatible/backorder), related items, kits.
- Outputs: rails with badges (“Alternative”, “Equivalent”, “Upgrade”).
- States: auto-trigger when OOS/incompatible; manual browse otherwise.
- Loading: card skeleton.

L) Policies & Trust
- Purpose: Risk reduction.
- Inputs: warranty, returns, authenticity, certifications.
- Outputs: compact summary with links.
- States: present/empty.

---

### 3) Interaction Flows (step lists)

Fitment flow
1. User opens PDP with unknown vehicle → Fitment Bar shows prompt.
2. User selects VIN/Plate/Manual → validate → show `fitmentStatus`.
3. If compatible → enable CTAs, show “Fits your vehicle”.
4. If incompatible → disable Buy Now, prefer Alternatives rail, explain why.
5. If requires verification → allow purchase with disclaimer.
6. Persist saved vehicle chip; allow clear/change.

OOS/backorder → Alternatives
1. Detect stockStatus in { out_of_stock, backorder, discontinued } OR incompatible.
2. Trigger alternatives fetch with reason; show inline loader in rail header.
3. Render alternatives with reason badge; keep primary CTAs visible but disabled or rerouted to Notify.

Add to Cart / Quote / Buy Now
1. Retail: Add to Cart → cart badge update; toast success; stay on PDP.
2. Pro: Add to Quote (if role=pro) → open quote drawer; confirm quantities.
3. Buy Now: immediate checkout; block if incompatible (unless allowed by policy).
4. Errors: show inline error near CTA plus toast; preserve qty.

Media fallback
1. Attempt to load main image; on error, show placeholder and log `media_error`.
2. If video/360 missing, hide tabs.

Region-based ETA
1. On city detect/set, recompute ETA; announce via ARIA live region.
2. Show range (minDays–maxDays) and pickup options if available.

---

### 4) Microcopy (EN + FA)

Notes: Right-to-left (FA) supported; ensure mirrored layout and bidi text handling.

Statuses and CTAs

| Context | Key | EN | FA |
|---|---|---|---|
| Fitment | compatible | Fits your vehicle | مناسب خودروی شماست |
| Fitment | incompatible | Does not fit your vehicle | مناسب خودروی شما نیست |
| Fitment | requires_verification | Verify compatibility | نیاز به تأیید سازگاری |
| Fitment | unknown | Compatibility unknown | سازگاری نامشخص |
| Stock | in_stock | In stock | موجود |
| Stock | low_stock | Only {count} left | فقط {count} عدد باقی مانده |
| Stock | out_of_stock | Out of stock | ناموجود |
| Stock | backorder | Available on backorder | قابل سفارش از تامین‌کننده |
| ETA | eta_days | Delivers in {min}-{max} days | تحویل در {min} تا {max} روز |
| Alternatives | auto_loaded | Showing alternatives due to {reason} | نمایش جایگزین‌ها به دلیل {reason} |
| Installer | book | Book installation | رزرو نصب |
| Warranty | summary | {months}-month warranty | گارانتی {months} ماهه |
| Returns | summary | {days}-day returns | بازگشت تا {days} روز |
| CTA | add_to_cart | Add to Cart | افزودن به سبد |
| CTA | buy_now | Buy Now | خرید فوری |
| CTA (pro) | add_to_quote | Add to Quote | افزودن به پیش‌فاکتور |
| Toast | added_to_cart | Added to cart | به سبد افزوده شد |
| Empty | no_reviews | No reviews yet | هنوز نظری ثبت نشده |
| Error | generic | Something went wrong. Please try again. | خطایی رخ داد. دوباره تلاش کنید. |

Helper/Placeholders

| Field | EN | FA |
|---|---|---|
| VIN | Enter VIN | شناسه VIN را وارد کنید |
| Plate | Enter plate number | شماره پلاک را وارد کنید |
| Manual | Select year, make, model... | سال، سازنده، مدل را انتخاب کنید... |
| Qty | Quantity | تعداد |

Empty/Recovery

| Area | EN | FA |
|---|---|---|
| Cross-Refs | No references available | مرجعی موجود نیست |
| Specs | Specifications not available | مشخصات در دسترس نیست |
| Alternatives | No alternatives found | جایگزینی یافت نشد |
| Installer | No slots available for this date | وقت خالی برای این تاریخ موجود نیست |

---

### 5) Event Tracking Plan (Analytics)

Event taxonomy & payload contracts (copy/paste-ready):

```json
{ "event": "pdp_view", "payload": { "sku": "OF-123", "category": "Filters", "compatible": true, "priceTier": "retail", "stockStatus": "in_stock" } }
```

```json
{ "event": "fitment_change", "payload": { "method": "vin", "result": "compatible", "vehicleId": "trim-8893" } }
```

```json
{ "event": "add_to_cart", "payload": { "sku": "OF-123", "qty": 2, "priceTier": "pro", "availability": { "stockStatus": "in_stock", "availableQty": 42 }, "etaType": "city", "compatible": true } }
```

```json
{ "event": "view_cross_reference", "payload": { "sku": "OF-123", "oemRefsCount": 3, "crossRefsCount": 5 } }
```

```json
{ "event": "view_alternatives", "payload": { "sku": "OF-123", "reason": "oos", "shown": 8 } }
```

```json
{ "event": "installer_booking_start", "payload": { "sku": "OF-123", "city": "Tehran", "slotId": "v-12-10:00" } }
```

```json
{ "event": "installer_booking_complete", "payload": { "sku": "OF-123", "city": "Tehran", "slotId": "v-12-10:00" } }
```

Conventions & timing
- Names: snake_case; event root keys fixed; payload keys stable; booleans not tri-state.
- Timing: `pdp_view` on first meaningful paint; `fitment_change` on result; `add_to_cart` on server 200/201; others on render.
- Deduping: session-level idempotency for repeated renders; include `requestId` when available.
- PII: no raw VIN/plate stored; only `vehicleId` tokens.

---

### 6) Accessibility Notes

- Roles: tabs (`role="tablist"/"tab"/"tabpanel"`), accordions (button+region), gallery modal (`role="dialog"`).
- Live regions: `aria-live="polite"` for stock/ETA/fitment announcements; announce only deltas.
- Focus: logical order—Fitment → Title → Price/CTAs → Media → Details; trap focus in modals; restore focus on close.
- Keyboard: gallery (Left/Right to navigate, Enter to zoom, Esc to close), accordions (Up/Down, Home/End), forms (Enter to submit).
- Contrast: 4.5:1 for text; 3:1 for large text/icons; focus visible at 3:1.
- SR copy: announce compatibility status, stock changes, and alternative triggers.

---

### 7) Visual & Content Guidelines

- Hierarchy: above the fold—brand/name, price, stock/fitment, media; below—refs/specs/reviews.
- Spacing: 8px grid; 24–32px between primary blocks; dense tables for specs/refs.
- Iconography/badges: authorized, OEM, best-seller, new, low-stock, verified purchase.
- Images: white/neutral background, 3–6 angles, 1200×1200 preferred, consistent scale; 360 when helpful.
- Video: 15–60s, captions required, mute by default, controls visible.
- SEO hooks: FAQ/HowTo sections link to full articles; use descriptive link text.

---

### 8) Acceptance Criteria (UX)

- All critical states (fitment, stock, ETA, alternatives, installer, reviews) have distinct copy and visuals.
- Mobile LCP element (title/price/media) is within initial viewport and not lazy-loaded.
- OOS/incompatible shows alternatives without dead-ends; user has a clear next step.
- All microcopy exists in EN and FA; extraction-ready for i18n.
- Keyboard-only users can complete: fitment, add to cart, open media modal, read specs, and access policies.
- Live regions announce fitment/stock/ETA changes without disrupting focus.


