# Parts & Inventory Integration - Phase 1 Acceptance Test Runbook

## 1. Executive Summary

### Purpose
This runbook provides comprehensive acceptance testing procedures to verify that Phase 1 of the Parts & Inventory Integration is functioning correctly in staging/production environments. The tests validate end-to-end functionality from backend APIs to frontend user interfaces.

### Preconditions
Before running these tests, ensure the following are in place:

- ✅ **Backend API Server**: Running on `http://localhost:8001` (or production URL)
- ✅ **Admin Panel**: Deployed and accessible at `http://localhost:5173` (or production URL)
- ✅ **Web Portal**: Deployed and accessible at `http://localhost:5174` (or production URL)
- ✅ **Database**: SQLite database with required tables (`parts`, `stock_levels`, `prices_new`, `part_categories`)
- ✅ **Admin Account**: Valid admin user credentials for panel access
- ✅ **Network Access**: Ability to make HTTP requests to all endpoints

### Test Scope
- Backend API health and CRUD operations
- Admin panel workflows (create/update parts, pricing, stock management)
- Public web workflows (search functionality, product detail pages)
- Logging and monitoring sanity checks
- Basic security validation (JWT enforcement on admin endpoints)

---

## 2. Test Matrix

| Scenario | Steps | Expected Result | Priority |
|----------|-------|-----------------|----------|
| **Health Check** | `curl GET /api/v1/health` | 200 OK, JSON `{"status":"ok"}` | Critical |
| **List Parts** | `curl GET /api/v1/parts/` | 200 OK, Array of parts with price/stock | Critical |
| **List Categories** | `curl GET /api/v1/parts/categories/` | 200 OK, Array of categories | Critical |
| **Create Part (Admin)** | `curl POST /api/v1/admin/parts/` (with JWT) | 201 Created, returns part object | Critical |
| **Update Price** | `curl PUT /api/v1/admin/parts/{id}/price` | 200 OK, returns updated price | Critical |
| **Update Stock** | `curl PUT /api/v1/admin/parts/{id}/stock` | 200 OK, returns updated stock | Critical |
| **Fetch Part Detail** | `curl GET /api/v1/parts/{id}` | 200 OK, includes nested price+stock | Critical |
| **Panel UI Create** | Create part in Admin Panel UI | Part appears in list with success message | High |
| **Panel UI Update** | Edit stock/price in panel | UI refreshes, values updated correctly | High |
| **Web Search** | Search for part on `/search` page | Part card displays with real price + stock | High |
| **Web Detail Page** | Open Product Detail Page (PDP) | Shows correct name, price, stock badge | High |
| **Admin Security** | Hit admin endpoints without JWT | Returns 401 Unauthorized | High |
| **Public Security** | Hit public endpoints without JWT | Returns 200 OK (no auth required) | Medium |
| **Log Monitoring** | Check backend logs | No 500 errors, proper audit trails | Medium |

---

## 3. Step-by-Step CLI Tests

### Prerequisites
```bash
# Set your environment variables
export API_BASE_URL="http://localhost:8001"
export ADMIN_PANEL_URL="http://localhost:5173"
export WEB_PORTAL_URL="http://localhost:5174"

# Optional: Set JWT token for admin operations
export ADMIN_JWT="your-jwt-token-here"
```

### Test 1: Health Check
```bash
curl -X GET "${API_BASE_URL}/health" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n"
```
**Expected**: 200 OK with JSON response containing status information

### Test 2: List Parts (Public API)
```bash
curl -X GET "${API_BASE_URL}/api/v1/parts/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 200 OK with array of parts, each containing `price` and `stock` objects

### Test 3: List Categories (Public API)
```bash
curl -X GET "${API_BASE_URL}/api/v1/parts/categories/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 200 OK with array of categories

### Test 4: Create Part (Admin API)
```bash
curl -X POST "${API_BASE_URL}/api/v1/admin/parts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ADMIN_JWT}" \
  -d '{
    "part_name": "Acceptance Test Brake Pad",
    "brand_oem": "TestBrand",
    "vehicle_make": "TestMake",
    "vehicle_model": "TestModel",
    "vehicle_trim": "2023",
    "category": "Brake System",
    "oem_code": "ACCEPTANCE-TEST-001",
    "status": "active"
  }' \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 201 Created with complete part object including ID

### Test 5: Update Price (Admin API)
```bash
# Replace {PART_ID} with actual part ID from previous test
curl -X PUT "${API_BASE_URL}/api/v1/admin/parts/{PART_ID}/price" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ADMIN_JWT}" \
  -d '{
    "list_price": "550000",
    "sale_price": "500000",
    "currency": "IRR"
  }' \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 200 OK with updated price object

### Test 6: Update Stock (Admin API)
```bash
# Replace {PART_ID} with actual part ID
curl -X PUT "${API_BASE_URL}/api/v1/admin/parts/{PART_ID}/stock" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ADMIN_JWT}" \
  -d '{
    "current_stock": 50,
    "reserved_quantity": 10,
    "min_stock_level": 15
  }' \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 200 OK with updated stock object

### Test 7: Fetch Part Detail (Public API)
```bash
# Replace {PART_ID} with actual part ID
curl -X GET "${API_BASE_URL}/api/v1/parts/{PART_ID}" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" | jq .
```
**Expected**: 200 OK with complete part object including nested `price` and `stock` objects

### Test 8: Security - Unauthorized Admin Access
```bash
curl -X POST "${API_BASE_URL}/api/v1/admin/parts/" \
  -H "Content-Type: application/json" \
  -d '{"part_name": "Unauthorized Test"}' \
  -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n"
```
**Expected**: 401 Unauthorized or 422 Unprocessable Content (validation error)

---

## 4. Admin Panel Screenshots Checklist

Capture the following screenshots to verify UI functionality:

### Screenshot 1: Part Creation Success
**Action**: Create a new part using the Admin Panel UI
**Capture**: 
- Admin Panel Parts page showing the newly created part in the list
- Success message/notification confirming creation
- Part details visible (name, brand, OEM code, status)

### Screenshot 2: Price/Stock Update Success
**Action**: Update price and stock for an existing part
**Capture**:
- Price modal showing updated values
- Stock modal showing updated quantities
- Parts list reflecting the changes (if visible)
- Success confirmation messages

### Screenshot 3: Clean Console After Operations
**Action**: Complete several CRUD operations in the Admin Panel
**Capture**:
- Browser Developer Tools Console (F12 → Console tab)
- Verify no JavaScript errors (red text)
- Verify no 500 Internal Server Error messages
- Optional: Network tab showing successful API calls

---

## 5. Public Web Screenshots Checklist

Capture the following screenshots to verify public-facing functionality:

### Screenshot 1: Search Results with Real Data
**Action**: Navigate to `/search` and search for a part
**Capture**:
- Search results page showing part cards
- Part cards displaying real prices (not mock data)
- Stock status indicators (In Stock/Out of Stock badges)
- Proper Persian number formatting for prices

### Screenshot 2: Product Detail Page (PDP)
**Action**: Click on a part to open its detail page
**Capture**:
- Product detail page with correct part information
- BuyBox component showing real price and stock
- Currency symbol display (تومان for IRR)
- Stock availability message
- No placeholder or mock data visible

### Screenshot 3: Clean Public Web Console
**Action**: Browse the public web portal and perform searches
**Capture**:
- Browser Developer Tools Console (F12 → Console tab)
- Verify no JavaScript errors
- Verify no API 500 errors in Network tab
- Verify successful API calls to parts endpoints

---

## 6. Logs & Monitoring

### Backend Log Checks
```bash
# Check for successful startup logs
grep -i "application startup complete" /path/to/backend/logs/*.log

# Check for table creation/validation logs
grep -i "critical tables" /path/to/backend/logs/*.log

# Check for recent errors (last 10 minutes)
grep -i "error\|exception\|traceback" /path/to/backend/logs/*.log | tail -20

# Check for parts-related audit logs
grep -i "parts audit" /path/to/backend/logs/*.log | tail -10
```

### Performance Monitoring
```bash
# Check API response times (should be < 500ms)
curl -w "Response Time: %{time_total}s\n" -o /dev/null -s "${API_BASE_URL}/api/v1/parts/"

# Check database query performance
grep -i "database_query" /path/to/backend/logs/*.log | grep -E "duration_ms:[0-9]+" | tail -5
```

### Expected Log Patterns
- ✅ `INFO: Application startup complete`
- ✅ `INFO: Critical tables created successfully` or `INFO: All critical tables exist`
- ✅ `INFO: Parts Audit: {"event": "part_created"...}`
- ✅ `INFO: Parts Performance: {"event": "api_request"...}`
- ❌ No `ERROR` or `CRITICAL` messages in the last 10 minutes
- ❌ No `AttributeError: 'PartPrice' object has no attribute 'effective_price'`

---

## 7. Security Checks

### Test Admin Endpoint Protection
```bash
# Test all admin endpoints without JWT
echo "Testing admin endpoints without authentication..."

# Create part without JWT
curl -X POST "${API_BASE_URL}/api/v1/admin/parts/" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s

# Update price without JWT  
curl -X PUT "${API_BASE_URL}/api/v1/admin/parts/1/price" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s

# Update stock without JWT
curl -X PUT "${API_BASE_URL}/api/v1/admin/parts/1/stock" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s
```
**Expected**: All should return 401 Unauthorized or 422 Unprocessable Content

### Test Public Endpoint Access
```bash
# Test public endpoints without JWT (should work)
echo "Testing public endpoints without authentication..."

# List parts without JWT
curl -X GET "${API_BASE_URL}/api/v1/parts/" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s

# List categories without JWT
curl -X GET "${API_BASE_URL}/api/v1/parts/categories/" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s

# Get part detail without JWT
curl -X GET "${API_BASE_URL}/api/v1/parts/1" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" -o /dev/null -s
```
**Expected**: All should return 200 OK

---

## 8. Acceptance Criteria

### Critical Criteria (Must Pass)
- [ ] **API Health**: All health checks return 200 OK
- [ ] **CRUD Operations**: Create, read, update operations work for parts, prices, and stock
- [ ] **Data Integrity**: Data created in admin panel appears correctly in public web
- [ ] **Response Structure**: All API responses include proper price and stock data
- [ ] **No 500 Errors**: Backend logs show no 500 Internal Server Errors
- [ ] **Frontend Functionality**: Admin panel and web portal load without JavaScript errors

### High Priority Criteria
- [ ] **Performance**: API response times < 500ms for standard operations
- [ ] **Security**: Admin endpoints properly protected, public endpoints accessible
- [ ] **UI Integration**: Real price/stock data displays in frontend components
- [ ] **Audit Logging**: All CRUD operations logged with proper audit trails

### Medium Priority Criteria
- [ ] **Error Handling**: Graceful error messages for invalid inputs
- [ ] **Data Validation**: Proper validation of price/stock values
- [ ] **Currency Display**: Correct currency symbols and formatting
- [ ] **Stock Logic**: Accurate calculation of available stock (current - reserved)

### Data Flow Validation
1. **Admin Creates Part** → Part appears in admin list ✅
2. **Admin Sets Price** → Price appears in admin and public views ✅
3. **Admin Sets Stock** → Stock status appears in admin and public views ✅
4. **Public Searches** → Part appears with real price/stock data ✅
5. **Public Views Detail** → PDP shows accurate pricing and availability ✅

---

## 9. Sign-off Checklist

### Pre-Test Setup
- [ ] Backend server running and accessible
- [ ] Admin panel deployed and accessible  
- [ ] Web portal deployed and accessible
- [ ] Admin user account available
- [ ] Database tables created and accessible

### API Testing
- [ ] Health check endpoint responds correctly
- [ ] Public API endpoints return expected data
- [ ] Admin API endpoints require authentication
- [ ] CRUD operations work for parts, prices, and stock
- [ ] Response times within acceptable limits (< 500ms)

### Frontend Testing
- [ ] Admin panel loads without errors
- [ ] Part creation works through UI
- [ ] Price/stock updates work through UI
- [ ] Web portal loads without errors
- [ ] Search functionality displays real data
- [ ] Product detail pages show accurate information

### Security Validation
- [ ] Admin endpoints protected (401 without JWT)
- [ ] Public endpoints accessible (200 without JWT)
- [ ] No sensitive data exposed in error messages

### Monitoring & Logs
- [ ] Backend logs show successful startup
- [ ] No critical errors in recent logs
- [ ] Audit trails generated for all operations
- [ ] Performance metrics within acceptable ranges

### Screenshots & Documentation
- [ ] Admin panel screenshots captured
- [ ] Public web screenshots captured
- [ ] Console error screenshots (should be clean)
- [ ] Test results documented

### Final Sign-off
- [ ] All critical criteria passed
- [ ] All high priority criteria passed
- [ ] No blocking issues identified
- [ ] System ready for production deployment

---

**Test Executed By**: _________________  
**Date**: _________________  
**Environment**: _________________  
**Version**: Phase 1 Integration  
**Status**: [ ] PASS [ ] FAIL [ ] CONDITIONAL PASS  

**Notes/Comments**:
```
[Space for test execution notes]
```

---

## Troubleshooting Guide

### Common Issues

**Issue**: 500 Internal Server Error on admin endpoints
- **Check**: Database tables exist (`stock_levels`, `prices_new`)
- **Fix**: Run `python scripts/create_stock_pricing_tables.py`

**Issue**: Parts not showing price/stock in public API
- **Check**: Parts have associated price/stock records
- **Fix**: Create price/stock records for test parts

**Issue**: Admin panel shows JavaScript errors
- **Check**: API base URL configuration
- **Fix**: Verify `VITE_API_BASE_URL` environment variable

**Issue**: Public web shows mock data instead of real prices
- **Check**: API integration in frontend components
- **Fix**: Verify Search.vue and BuyBox.vue are using real API data

**Issue**: Authentication errors on admin endpoints
- **Check**: JWT token validity and format
- **Fix**: Ensure proper Bearer token format: `Authorization: Bearer <token>`
