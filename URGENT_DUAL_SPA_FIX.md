# 🚨 URGENT: Fix Dual SPA Deployment

## Current Problem
- Server at http://5.223.59.155/ shows old admin panel at root `/`
- No customer portal deployed
- Admin panel not at `/panel/` path
- Asset paths incorrect (`/assets/` instead of `/panel/assets/`)

## Immediate Fix Steps

### Step 1: SSH into the server
```bash
ssh root@5.223.59.155
# or use your SSH key/credentials
```

### Step 2: Navigate to project directory
```bash
cd /opt/china-car-parts
```

### Step 3: Pull latest changes
```bash
git pull origin main
```

### Step 4: Build Admin Panel with correct base path
```bash
cd app/frontend/panel
npm install
npm run build:panel
```

### Step 5: Build Customer Portal
```bash
cd ../web
npm install
npm run build
```

### Step 6: Update Nginx configuration
```bash
cd /opt/china-car-parts
cp deployment/configs/nginx-production.conf /etc/nginx/sites-available/china-car-parts
```

### Step 7: Test and reload Nginx
```bash
nginx -t
systemctl reload nginx
```

### Step 8: Restart services
```bash
systemctl restart china-car-parts-api
systemctl restart china-car-parts-bot
```

### Step 9: Verify deployment
```bash
# Test Admin Panel at /panel/
curl http://localhost/panel/ | grep "Admin Panel"

# Test Customer Portal at /
curl http://localhost/ | grep "Customer Portal"

# Test API
curl http://localhost/api/v1/health
```

## Expected Results After Fix

- **Admin Panel**: http://5.223.59.155/panel/ (with /panel/assets/ paths)
- **Customer Portal**: http://5.223.59.155/ (with /assets/ paths)
- **API**: http://5.223.59.155/api/v1/ (unchanged)

## Quick One-Liner Fix

If you have SSH access, run this single command:

```bash
ssh root@5.223.59.155 "cd /opt/china-car-parts && git pull origin main && cd app/frontend/panel && npm install && npm run build:panel && cd ../web && npm install && npm run build && cd ../../.. && cp deployment/configs/nginx-production.conf /etc/nginx/sites-available/china-car-parts && nginx -t && systemctl reload nginx && systemctl restart china-car-parts-api && systemctl restart china-car-parts-bot"
```

## Verification Commands

After running the fix, test these URLs:

1. **Customer Portal**: http://5.223.59.155/
   - Should show "Chinese Auto Parts - Customer Portal"
   - Should have assets at `/assets/`

2. **Admin Panel**: http://5.223.59.155/panel/
   - Should show "Chinese Auto Parts - Admin Panel"  
   - Should have assets at `/panel/assets/`

3. **API Health**: http://5.223.59.155/api/v1/health
   - Should return healthy status
