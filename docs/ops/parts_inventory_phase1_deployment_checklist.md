# Parts & Inventory Integration - Phase 1 Production Deployment Checklist

## 1. Overview

### Purpose
Safely deploy Phase 1 (Parts & Inventory Integration) to production with full blue/green deployment strategy and comprehensive validation.

### Strategy
Blue/Green deployment with rollback safety, ensuring zero-downtime deployment and immediate rollback capability.

### Preconditions
- ✅ All acceptance tests passed in staging environment
- ✅ Seed data prepared and validated
- ✅ Database migrations tested and verified idempotent
- ✅ Frontend builds optimized and tested
- ✅ API endpoints validated with real data

### Environment Details
- **Production Server**: `5.223.41.154`
- **Backend API**: Port 8001
- **Admin Panel**: Port 5173
- **Web Portal**: Port 5174
- **Database**: SQLite (`data/app.db`)

---

## 2. Deployment Plan (Blue/Green)

### Phase 1: Pre-Deployment Setup
- [ ] **Backup Production Database**
  ```bash
  ssh root@5.223.41.154 "cp /root/china-car-parts/data/app.db /root/china-car-parts/data/app.db.backup.$(date +%Y%m%d_%H%M%S)"
  ```

- [ ] **Verify Blue Environment Status**
  ```bash
  curl -i http://5.223.41.154/api/v1/health
  # Expected: 200 OK
  ```

- [ ] **Prepare Green Environment Directory**
  ```bash
  ssh root@5.223.41.154 "mkdir -p /root/china-car-parts-green"
  ```

### Phase 2: Code Deployment
- [ ] **Deploy Backend Code to Green**
  ```bash
  # Pull latest code to green environment
  ssh root@5.223.41.154 "cd /root/china-car-parts-green && git clone https://github.com/your-repo/china-car-parts.git ."
  ssh root@5.223.41.154 "cd /root/china-car-parts-green && git checkout main && git pull origin main"
  ```

- [ ] **Run Database Migrations (Idempotent)**
  ```bash
  ssh root@5.223.41.154 "cd /root/china-car-parts-green && python scripts/create_stock_pricing_tables.py"
  # Expected: "✅ All required tables already exist!" or successful creation
  ```

- [ ] **Build Frontend Applications**
  ```bash
  # Build Admin Panel
  ssh root@5.223.41.154 "cd /root/china-car-parts-green/app/frontend/panel && npm ci && npm run build"
  
  # Build Web Portal
  ssh root@5.223.41.154 "cd /root/china-car-parts-green/app/frontend/web && npm ci && npm run build"
  ```

### Phase 3: Green Environment Setup
- [ ] **Start Green Backend Service**
  ```bash
  ssh root@5.223.41.154 "cd /root/china-car-parts-green && nohup python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8002 > backend-green.log 2>&1 &"
  ```

- [ ] **Verify Green Backend Health**
  ```bash
  curl -i http://5.223.41.154:8002/api/v1/health
  # Expected: 200 OK with {"status":"healthy"}
  ```

### Phase 4: Smoke Testing (Green Environment)
- [ ] **Run Complete Smoke Test Suite**
  ```bash
  ssh root@5.223.41.154 "cd /root/china-car-parts-green && python scripts/smoke_test_parts_integration.py --host http://5.223.41.154:8002 --verbose"
  # Expected: All 15 tests PASSED
  ```

### Phase 5: Traffic Switch (Blue → Green)
- [ ] **Update Nginx Configuration**
  ```bash
  ssh root@5.223.41.154 "cp /etc/nginx/sites-available/china-car-parts /etc/nginx/sites-available/china-car-parts.backup"
  # Update upstream to point to green environment (port 8002)
  ssh root@5.223.41.154 "systemctl reload nginx"
  ```

- [ ] **Verify Traffic Routing**
  ```bash
  curl -i http://5.223.41.154/api/v1/health
  # Expected: 200 OK from green environment
  ```

### Phase 6: Blue Environment Cleanup
- [ ] **Keep Blue Environment on Standby**
  ```bash
  # Keep blue backend running on port 8001 for 24 hours
  # Archive after successful green validation
  ```

---

## 3. Smoke Test Sheet

Run these quick checks immediately after deployment:

### 3.1 Backend API Tests
- [ ] **Health Check**
  ```bash
  curl -i http://5.223.41.154/api/v1/health
  # Expected: HTTP/1.1 200 OK, {"status":"healthy"}
  ```

- [ ] **Parts List (Public API)**
  ```bash
  curl -i http://5.223.41.154/api/v1/parts/
  # Expected: HTTP/1.1 200 OK, JSON array with parts data
  ```

- [ ] **Categories List**
  ```bash
  curl -i http://5.223.41.154/api/v1/parts/categories/
  # Expected: HTTP/1.1 200 OK, JSON array with categories
  ```

- [ ] **Admin Parts Creation (if auth available)**
  ```bash
  curl -i -X POST http://5.223.41.154/api/v1/admin/parts/ \
    -H "Content-Type: application/json" \
    -d '{"part_name": "Deployment Test Part", "brand_oem": "TestBrand", "vehicle_make": "TestMake", "vehicle_model": "TestModel", "category": "Test Category", "oem_code": "DEPLOY-001", "status": "active"}'
  # Expected: HTTP/1.1 200 OK or 422 Unprocessable Content (validation)
  ```

- [ ] **Part Detail Retrieval**
  ```bash
  curl -i http://5.223.41.154/api/v1/parts/1
  # Expected: HTTP/1.1 200 OK with nested price/stock data
  ```

### 3.2 Frontend Tests
- [ ] **Web Portal Homepage**
  ```bash
  curl -i http://5.223.41.154/
  # Expected: HTTP/1.1 200 OK, HTML content with Persian interface
  ```

- [ ] **Search Page Load**
  ```bash
  curl -i http://5.223.41.154/search
  # Expected: HTTP/1.1 200 OK, search interface loads
  ```

- [ ] **Admin Panel Access**
  ```bash
  curl -i http://5.223.41.154/panel/
  # Expected: HTTP/1.1 200 OK, admin login page loads
  ```

### 3.3 Data Validation
- [ ] **Verify Real Data Display**
  - Open http://5.223.41.154/search in browser
  - Confirm at least 1 product shows with price and stock information
  - Expected: Product card displays "400,000 تومان" and "موجودی: X عدد"

- [ ] **Admin Panel Functionality**
  - Open http://5.223.41.154/panel/ in browser
  - Confirm login page loads without console errors
  - Expected: Clean console, no JavaScript errors

### 3.4 Performance Validation
- [ ] **API Response Time**
  ```bash
  time curl -s http://5.223.41.154/api/v1/parts/ > /dev/null
  # Expected: < 1 second response time
  ```

- [ ] **Frontend Load Time**
  - Open http://5.223.41.154/ in browser
  - Expected: Page loads completely within 3 seconds

---

## 4. Monitoring Hooks

### 4.1 Performance Monitoring
- [ ] **Enable Latency Monitoring**
  ```bash
  # Monitor API response times
  # Alert if p95 latency > 500ms
  ```

- [ ] **Track HTTP Status Codes**
  ```bash
  # Monitor 4xx/5xx rates in access logs
  # Alert if error rate > 5%
  ```

### 4.2 Database Monitoring
- [ ] **Monitor DB Error Rate**
  ```bash
  # Track database connection errors
  # Alert if error rate > 1%
  ```

- [ ] **Monitor Slow Queries**
  ```bash
  # Track queries taking > 100ms
  # Alert if slow query rate > 10%
  ```

### 4.3 Application Monitoring
- [ ] **Monitor CORS/Preflight Errors**
  ```bash
  # Track OPTIONS request failures
  # Alert if CORS errors detected
  ```

- [ ] **Monitor Authentication Failures**
  ```bash
  # Track 401/403 responses
  # Alert if auth failure rate > 20%
  ```

### 4.4 Log Monitoring
- [ ] **Check for 500 Errors**
  ```bash
  ssh root@5.223.41.154 "tail -f /root/china-car-parts/backend.log | grep '500'"
  # Expected: No 500 errors during normal operation
  ```

- [ ] **Monitor Startup Errors**
  ```bash
  ssh root@5.223.41.154 "journalctl -u china-car-parts -f"
  # Expected: Clean startup, no critical errors
  ```

---

## 5. Seed Data Checklist

### 5.1 Database Verification
- [ ] **Verify Required Tables Exist**
  ```bash
  ssh root@5.223.41.154 "sqlite3 /root/china-car-parts/data/app.db '.tables' | grep -E '(parts|stock_levels|prices_new|part_categories)'"
  # Expected: All required tables present
  ```

- [ ] **Verify Data Relationships**
  ```bash
  ssh root@5.223.41.154 "sqlite3 /root/china-car-parts/data/app.db 'SELECT COUNT(*) FROM parts;'"
  # Expected: At least 20 parts in database
  ```

### 5.2 Seed Data Validation
- [ ] **Insert Test Parts (if needed)**
  ```bash
  curl -i -X POST http://5.223.41.154/api/v1/admin/parts/ \
    -H "Content-Type: application/json" \
    -d '{"part_name": "Production Test Brake Pad", "brand_oem": "ProductionBrand", "vehicle_make": "ProductionMake", "vehicle_model": "ProductionModel", "category": "Brake System", "oem_code": "PROD-001", "status": "active"}'
  ```

- [ ] **Set Price for Test Part**
  ```bash
  curl -i -X PUT http://5.223.41.154/api/v1/admin/parts/{PART_ID}/price \
    -H "Content-Type: application/json" \
    -d '{"list_price": "500000", "sale_price": "450000", "currency": "IRR"}'
  ```

- [ ] **Set Stock for Test Part**
  ```bash
  curl -i -X PUT http://5.223.41.154/api/v1/admin/parts/{PART_ID}/stock \
    -H "Content-Type: application/json" \
    -d '{"current_stock": 100, "reserved_quantity": 10, "min_stock_level": 20}'
  ```

### 5.3 Frontend Data Verification
- [ ] **Verify Public Search Shows Data**
  - Open http://5.223.41.154/search
  - Confirm products display with real price and stock
  - Expected: At least 1 product shows "450,000 تومان" and stock count

- [ ] **Verify PDP Shows Complete Data**
  - Click on a product to view details
  - Confirm price, stock, and specifications display
  - Expected: Complete product information with pricing

- [ ] **Verify Admin Panel Shows Data**
  - Access admin panel (if authentication working)
  - Confirm parts list shows created products
  - Expected: Parts visible with editable price/stock fields

---

## 6. Rollback Plan

### 6.1 Immediate Rollback (Traffic Switch)
- [ ] **Switch Traffic Back to Blue**
  ```bash
  # Restore Nginx configuration to point to blue environment
  ssh root@5.223.41.154 "cp /etc/nginx/sites-available/china-car-parts.backup /etc/nginx/sites-available/china-car-parts"
  ssh root@5.223.41.154 "systemctl reload nginx"
  ```

- [ ] **Verify Rollback Success**
  ```bash
  curl -i http://5.223.41.154/api/v1/health
  # Expected: 200 OK from blue environment
  ```

### 6.2 Database Rollback (If Needed)
- [ ] **Restore Database from Backup**
  ```bash
  ssh root@5.223.41.154 "cp /root/china-car-parts/data/app.db.backup.$(date +%Y%m%d_%H%M%S) /root/china-car-parts/data/app.db"
  ```

- [ ] **Restart Blue Backend Service**
  ```bash
  ssh root@5.223.41.154 "systemctl restart china-car-parts"
  ```

### 6.3 Rollback Documentation
- [ ] **Document Failure Cause**
  ```bash
  # Log rollback reason in ops log
  echo "$(date): Rollback executed - [REASON]" >> /root/china-car-parts/ops.log
  ```

- [ ] **Notify Team**
  ```bash
  # Send notification to team about rollback
  # Include failure details and next steps
  ```

### 6.4 Green Environment Cleanup
- [ ] **Stop Green Services**
  ```bash
  ssh root@5.223.41.154 "pkill -f 'uvicorn.*port.*8002'"
  ```

- [ ] **Archive Green Environment**
  ```bash
  ssh root@5.223.41.154 "mv /root/china-car-parts-green /root/china-car-parts-green.archived.$(date +%Y%m%d_%H%M%S)"
  ```

---

## 7. Final Sign-off

### 7.1 Technical Validation
- [ ] **Smoke Tests Passed**
  - All 7 smoke test checks completed successfully
  - No 500 errors in backend logs
  - Frontend loads without console errors

- [ ] **Monitoring Green**
  - All monitoring hooks enabled and functioning
  - No critical alerts triggered
  - Performance metrics within acceptable ranges

- [ ] **Seed Data Visible**
  - At least 3 parts with complete data (price, stock, categories)
  - Data displays correctly in public search and PDP
  - Admin panel shows parts with editable fields

### 7.2 Operational Validation
- [ ] **Blue Environment on Standby**
  - Blue environment remains accessible for 24 hours
  - Rollback capability verified and documented
  - Monitoring continues for both environments

- [ ] **Documentation Updated**
  - Deployment checklist completed and signed off
  - All changes documented in ops log
  - Team notified of successful deployment

### 7.3 Production Readiness Confirmation
- [ ] **System Performance**
  - API response times < 1 second
  - Frontend load times < 3 seconds
  - Database queries optimized and fast

- [ ] **Error Handling**
  - Graceful error responses (no 500s)
  - Proper validation messages
  - Clean console output

- [ ] **User Experience**
  - Persian interface fully functional
  - Search and filtering working correctly
  - Product detail pages complete

---

## 8. Post-Deployment Tasks

### 8.1 Monitoring (First 24 Hours)
- [ ] **Continuous Monitoring**
  ```bash
  # Monitor logs every 30 minutes for first 4 hours
  ssh root@5.223.41.154 "tail -100 /root/china-car-parts/backend.log | grep -E '(ERROR|500|Exception)'"
  ```

- [ ] **Performance Checks**
  ```bash
  # Check response times every hour
  time curl -s http://5.223.41.154/api/v1/parts/ > /dev/null
  ```

### 8.2 User Acceptance Testing
- [ ] **Internal Team Testing**
  - Test admin panel functionality
  - Verify public search and product details
  - Confirm all user workflows function correctly

- [ ] **Stakeholder Validation**
  - Demo key features to stakeholders
  - Confirm Persian interface quality
  - Validate business requirements met

### 8.3 Documentation Updates
- [ ] **Update Deployment Logs**
  ```bash
  echo "$(date): Phase 1 deployment completed successfully" >> /root/china-car-parts/deployment.log
  ```

- [ ] **Archive Blue Environment**
  ```bash
  # After 24 hours of successful operation
  ssh root@5.223.41.154 "systemctl stop china-car-parts-blue"
  ```

---

## 9. Emergency Contacts & Procedures

### 9.1 Emergency Contacts
- **DevOps Lead**: [Contact Information]
- **Backend Developer**: [Contact Information]
- **Frontend Developer**: [Contact Information]
- **Database Administrator**: [Contact Information]

### 9.2 Emergency Procedures
- **Critical Issues**: Immediate rollback to blue environment
- **Performance Issues**: Scale resources or investigate bottlenecks
- **Data Issues**: Restore from backup and investigate root cause
- **Security Issues**: Immediate service shutdown and investigation

---

## 10. Deployment Checklist Summary

### Pre-Deployment
- [ ] Backup production database
- [ ] Verify blue environment status
- [ ] Prepare green environment

### Deployment
- [ ] Deploy code to green environment
- [ ] Run database migrations
- [ ] Build frontend applications
- [ ] Start green services
- [ ] Run smoke tests

### Go-Live
- [ ] Switch traffic to green
- [ ] Verify traffic routing
- [ ] Monitor for issues

### Post-Deployment
- [ ] Complete monitoring setup
- [ ] Validate seed data
- [ ] Perform user acceptance testing
- [ ] Keep blue on standby for 24 hours

### Sign-off
- [ ] All smoke tests passed
- [ ] Monitoring green
- [ ] Seed data validated
- [ ] Documentation complete

---

**Deployment Checklist Completed By**: ________________

**Date**: ________________

**Time**: ________________

**Signature**: ________________

---

*This deployment checklist ensures safe, zero-downtime deployment of Parts & Inventory Integration Phase 1 with comprehensive validation and rollback capabilities.*
