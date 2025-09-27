# Parts & Inventory Integration - Phase 1 Smoke Test

## 1. Purpose

**One-page smoke sheet** to quickly confirm buyer + vendor flows are working after each deployment.  
**Target time**: < 10 minutes  
**Goal**: Verify core parts & inventory functionality is operational

---

## 2. Critical API Tests (curl, copy-paste)

### 1. Health Check
```bash
curl -i http://<HOST>/api/v1/health
```
**→ Expect**: `200 OK`, `{"status":"ok"}`

### 2. List Parts (empty or seeded)
```bash
curl -i http://<HOST>/api/v1/parts
```
**→ Expect**: `200 OK`, `[]` or array of parts with price/stock objects

### 3. Create Part (admin, JWT)
```bash
curl -i -X POST http://<HOST>/api/v1/admin/parts \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "part_name": "Smoke Test Brake Pad",
    "brand_oem": "TestBrand",
    "vehicle_make": "TestMake",
    "vehicle_model": "TestModel",
    "category": "Brake System",
    "oem_code": "SMOKE-001",
    "status": "active"
  }'
```
**→ Expect**: `201 Created`, JSON with `part_id`

### 4. Set Stock (admin)
```bash
curl -i -X PUT http://<HOST>/api/v1/admin/parts/{id}/stock \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_stock": 5,
    "reserved_quantity": 0,
    "min_stock_level": 2
  }'
```
**→ Expect**: `200 OK`

### 5. Set Price (admin)
```bash
curl -i -X PUT http://<HOST>/api/v1/admin/parts/{id}/price \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "list_price": "450000",
    "sale_price": "400000",
    "currency": "IRR"
  }'
```
**→ Expect**: `200 OK`

### 6. Get Part Detail
```bash
curl -i http://<HOST>/api/v1/parts/{id}
```
**→ Expect**: `200 OK`, includes `"stock": {"in_stock": true}` and `"price": {"effective_price": "400000"}`

### 7. Security Check (no JWT)
```bash
curl -i -X POST http://<HOST>/api/v1/admin/parts \
  -H "Content-Type: application/json" \
  -d '{"part_name":"Unauthorized Test"}'
```
**→ Expect**: `401 Unauthorized` or `422 Unprocessable Content`

---

## 3. Frontend Checks

### Admin Panel
- **Action**: Create part + set stock through UI
- **Verify**: Part appears in list, no console errors
- **Time**: ~2 minutes

### Web Portal  
- **Action**: Search for created part
- **Verify**: Card visible with correct name + stock badge, no console errors
- **Time**: ~2 minutes

---

## 4. Acceptance Criteria

- ✅ All curl commands return expected status codes
- ✅ Part created in admin is visible on web search/PDP  
- ✅ No 500 errors in logs or browser console
- ✅ Real price/stock data displays (not mock data)
- ✅ Admin endpoints protected, public endpoints open

---

## 5. Sign-off

| Check | Status |
|-------|--------|
| [ ] API PASS | □ |
| [ ] Admin Panel PASS | □ |
| [ ] Web PASS | □ |
| [ ] Logs clean | □ |

**Overall**: [ ] PASS [ ] FAIL

**Notes**: _________________________

---

## Quick Environment Setup

```bash
# Set your environment
export HOST="http://localhost:8001"  # or production URL
export TOKEN="your-jwt-token"        # admin JWT token

# Run all API tests
curl -i $HOST/api/v1/health
curl -i $HOST/api/v1/parts
# ... (copy commands above)
```

**Total time**: ~8 minutes  
**Critical path**: API → Admin UI → Web UI → Logs
