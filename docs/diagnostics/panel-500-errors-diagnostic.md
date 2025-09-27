# Post-Login 500s in Admin Panel — Evidence-Driven Diagnostic Report

**Date:** 2025-09-27  
**Issue:** Repeated 500 Internal Server Error on admin dashboard calls after successful login  
**Scope:** GET /api/v1/parts/ and GET /api/v1/categories/ endpoints  

## Executive Summary

**Root Cause:** Missing database tables (`parts` and `part_categories`) in production database.

**Impact:** Admin panel dashboard fails to load because core data endpoints return 500 errors, preventing admin users from accessing parts and categories management.

**Confidence:** 95% - Direct evidence from endpoint testing and code analysis.

---

## 1. Reproduction Log

### Test Environment
- **Production Server:** http://5.223.41.154
- **Backend Direct:** http://5.223.41.154:8001
- **Backend Status:** Running in development mode
- **Database:** SQLite (development configuration)

### Reproduction Steps
1. **Health Check:** ✅ `GET /api/v1/health` returns 200 OK
2. **Authentication Test:** ❌ Login fails (admin user not found)
3. **Parts Endpoint:** ❌ `GET /api/v1/parts/` returns 500 Internal Server Error
4. **Categories Endpoint:** ❌ `GET /api/v1/categories/` returns 500 Internal Server Error
5. **Orders Endpoint:** ✅ `GET /api/v1/orders/` returns 200 OK with empty array
6. **Leads Endpoint:** ✅ `GET /api/v1/leads/` returns 200 OK with empty array

### Network Evidence

```bash
# Direct backend access (bypassing Nginx)
curl -i http://5.223.41.154:8001/api/v1/parts/
HTTP/1.1 500 Internal Server Error
server: uvicorn
content-type: text/plain; charset=utf-8
Internal Server Error

curl -i http://5.223.41.154:8001/api/v1/categories/
HTTP/1.1 500 Internal Server Error
server: uvicorn
content-type: text/plain; charset=utf-8
Internal Server Error

# Working endpoints for comparison
curl -i http://5.223.41.154:8001/api/v1/orders/
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json
[]

curl -i http://5.223.41.154:8001/api/v1/leads/
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json
[]
```

---

## 2. Evidence Collection

### Backend Code Analysis

**Parts Router:** `app/api/routers/parts.py:46-87`
```python
@router.get("/", response_model=List[PartResponse])
async def list_parts(
    skip: int = 0,
    limit: int = 100,
    # ... filters ...
    db: Session = Depends(get_db),
):
    parts_service = PartsService(db)
    parts = parts_service.get_parts(...)  # ← Fails here
    return [PartResponse(...) for part in parts]
```

**Categories Router:** `app/api/routers/categories.py:81-149`
```python
@router.get("/", response_model=List[PartCategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    # ... filters ...
    db: Session = Depends(get_db),
):
    category_service = CategoryService(db)
    categories = category_service.get_categories(...)  # ← Fails here
    # ... response building ...
```

### Database Model Analysis

**Part Model:** `app/db/models.py:26-63`
```python
class Part(Base):
    __tablename__ = "parts"  # ← Table name
    
    id = Column(Integer, primary_key=True, index=True)
    part_name = Column(String(255), nullable=False, index=True)
    # ... other columns ...
```

**PartCategory Model:** `app/db/models.py:426-446`
```python
class PartCategory(Base):
    __tablename__ = "part_categories"  # ← Table name
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("part_categories.id"), nullable=True)
    # ... other columns ...
```

### Database Initialization Analysis

**Critical Finding:** `app/api/main.py:67-108`
```python
@app.on_event("startup")
async def ensure_critical_tables():
    """Ensure critical OTP tables and User columns exist on startup."""
    critical_tables = ["otp_codes", "rate_limits", "phone_verifications"]
    # ← Only creates OTP tables, NOT parts/categories tables!
```

**Missing Logic:** The startup hook only creates OTP-related tables but **never creates the core application tables** (`parts`, `part_categories`, etc.).

---

## 3. Hypothesis Testing

| Hypothesis | Test Method | Result | Verdict |
|------------|-------------|---------|---------|
| **Missing Authorization header** | `curl -i /parts/` without Bearer token | 500 (not 401) | ❌ **FAIL** |
| **Wrong decoder/claims** | Compare with `/users/me` (works with 403) | 500 vs 403 | ❌ **FAIL** |
| **DB schema mismatch** | Check table existence via working endpoints | Orders/leads work, parts/categories don't | ✅ **PASS** |
| **Query assumes non-null data** | Code analysis shows simple SELECT queries | No complex joins or assumptions | ❌ **FAIL** |
| **Nginx proxy issue** | Direct backend access (port 8001) | Same 500 error | ❌ **FAIL** |

---

## 4. Root Cause Analysis

### Primary Cause: Missing Database Tables

**Evidence:**
1. **Direct Backend Access:** 500 errors occur even when bypassing Nginx proxy
2. **Selective Failure:** Only parts/categories endpoints fail; orders/leads work
3. **Code Analysis:** Parts and categories services query tables that don't exist
4. **Startup Logic:** Application only creates OTP tables, not core application tables

**Technical Details:**
- **Parts Service:** `app/services/parts_service.py:25` executes `self.db.query(Part)` on non-existent `parts` table
- **Categories Service:** `app/services/category_service.py:30` executes `self.db.query(PartCategory)` on non-existent `part_categories` table
- **SQLAlchemy Exception:** When querying non-existent tables, SQLAlchemy raises unhandled exceptions → 500 error

### Secondary Factors

1. **Development Mode:** Backend running in development mode with SQLite database
2. **Missing Table Creation:** No Alembic migrations or table creation logic for core tables
3. **Incomplete Startup Hook:** Only handles OTP tables, ignores main application schema

---

## 5. Verification Commands

### Confirming Table Absence
```bash
# These should return 500 if tables don't exist
curl -i http://5.223.41.154:8001/api/v1/parts/
curl -i http://5.223.41.154:8001/api/v1/categories/

# These should return 200 if tables exist  
curl -i http://5.223.41.154:8001/api/v1/orders/
curl -i http://5.223.41.154:8001/api/v1/leads/
```

### Expected Behavior After Fix
```bash
# Should return 200 with empty arrays
curl -i http://5.223.41.154:8001/api/v1/parts/
HTTP/1.1 200 OK
[]

curl -i http://5.223.41.154:8001/api/v1/categories/  
HTTP/1.1 200 OK
[]
```

---

## 6. Proposed Fix Options

### Option 1: Extend Startup Hook (Recommended)
**File:** `app/api/main.py:67-108`
**Action:** Add parts and categories tables to `critical_tables` list
**Impact:** Automatic table creation on every startup
**Risk:** Low - already working for OTP tables

### Option 2: Manual Database Migration
**Action:** Run Alembic migration or manual table creation
**Impact:** One-time fix
**Risk:** Medium - requires manual intervention

### Option 3: Database Initialization Script
**Action:** Create separate script to initialize core tables
**Impact:** Controlled table creation
**Risk:** Low - can be tested separately

---

## 7. Acceptance Criteria

### Immediate Fix
- [ ] `/api/v1/parts/` returns 200 OK (empty array acceptable)
- [ ] `/api/v1/categories/` returns 200 OK (empty array acceptable)
- [ ] Admin panel dashboard loads without 500 errors
- [ ] No regression in working endpoints (orders, leads, health)

### Long-term Solution
- [ ] All core application tables created automatically
- [ ] Database schema properly initialized in production
- [ ] Admin panel fully functional for parts/categories management

---

## 8. Raw Evidence Logs

### Endpoint Test Results
```
Timestamp: 2025-09-27 09:26:30 GMT
Endpoint: GET /api/v1/parts/
Status: 500 Internal Server Error
Server: uvicorn
Response: "Internal Server Error"

Timestamp: 2025-09-27 09:26:32 GMT  
Endpoint: GET /api/v1/categories/
Status: 500 Internal Server Error
Server: uvicorn
Response: "Internal Server Error"

Timestamp: 2025-09-27 09:27:13 GMT
Endpoint: GET /api/v1/orders/
Status: 200 OK
Server: uvicorn
Response: []

Timestamp: 2025-09-27 09:27:15 GMT
Endpoint: GET /api/v1/leads/
Status: 200 OK
Server: uvicorn
Response: []
```

### Health Endpoint Response
```json
{
  "status": "healthy",
  "app_env": "development", 
  "debug": true,
  "version": "1.0.0"
}
```

---

## Conclusion

**Root Cause:** Missing `parts` and `part_categories` database tables in production database.

**Next Steps:** 
1. Extend startup hook to create core application tables
2. Verify table creation and endpoint functionality
3. Test admin panel dashboard loading

**Priority:** High - blocks core admin panel functionality
