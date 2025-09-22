#!/bin/bash

# 🔧 Fix Dual SPA Deployment Script
# This script manually applies the dual SPA architecture to the production server

set -e

echo "🔧 Fixing Dual SPA Deployment"
echo "============================="

# Server details (replace with actual server details)
SERVER_HOST="5.223.59.155"
SERVER_USER="root"  # Adjust as needed
SERVER_PASSWORD=""  # This should be set via environment variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Deployment Fix Plan:${NC}"
echo "1. Update server with latest code"
echo "2. Build both SPAs with correct base paths"
echo "3. Update Nginx configuration for dual SPAs"
echo "4. Restart services"
echo "5. Verify deployment"

echo -e "\n${YELLOW}⚠️ Note: This script assumes SSH access to the server${NC}"
echo -e "${YELLOW}⚠️ Make sure to set SERVER_PASSWORD environment variable${NC}"

# Check if we have server access
if [ -z "$SERVER_PASSWORD" ]; then
    echo -e "${RED}❌ SERVER_PASSWORD not set. Please set it and run again.${NC}"
    echo "Example: SERVER_PASSWORD=yourpassword ./fix_dual_spa_deployment.sh"
    exit 1
fi

echo -e "\n${BLUE}🚀 Starting deployment fix...${NC}"

# Create deployment script for the server
cat > server_deploy_script.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Server-side deployment fix starting..."

# Navigate to project directory
cd /opt/china-car-parts

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Build Admin Panel with /panel/ base path
echo "🏗️ Building Admin Panel with /panel/ base path..."
cd app/frontend/panel
npm install
npm run build:panel

# Build Customer Portal with / base path
echo "🏗️ Building Customer Portal with / base path..."
cd ../web
npm install
npm run build

# Go back to project root
cd ../../..

# Update Nginx configuration
echo "🌐 Updating Nginx configuration..."
cp deployment/configs/nginx-production.conf /etc/nginx/sites-available/china-car-parts

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
systemctl reload nginx

# Restart API service
echo "🔄 Restarting API service..."
systemctl restart china-car-parts-api

# Restart Bot service
echo "🔄 Restarting Bot service..."
systemctl restart china-car-parts-bot

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Health check
echo "🏥 Running health check..."
if curl -f http://localhost:8001/api/v1/health > /dev/null; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
    exit 1
fi

echo "✅ Deployment fix completed successfully!"
EOF

# Copy script to server
echo "📤 Copying deployment script to server..."
sshpass -p "$SERVER_PASSWORD" scp server_deploy_script.sh $SERVER_USER@$SERVER_HOST:/tmp/

# Execute script on server
echo "🚀 Executing deployment on server..."
sshpass -p "$SERVER_PASSWORD" ssh $SERVER_USER@$SERVER_HOST "chmod +x /tmp/server_deploy_script.sh && /tmp/server_deploy_script.sh"

# Clean up local script
rm server_deploy_script.sh

echo -e "\n${GREEN}🎉 Deployment fix completed!${NC}"
echo -e "${BLUE}📋 Verification:${NC}"
echo "  - Admin Panel should be at: http://$SERVER_HOST/panel/"
echo "  - Customer Portal should be at: http://$SERVER_HOST/"
echo "  - API should be at: http://$SERVER_HOST/api/v1/"

echo -e "\n${YELLOW}🧪 Testing deployment...${NC}"

# Test the deployment
echo "Testing Admin Panel at /panel/:"
curl -s http://$SERVER_HOST/panel/ | head -5

echo -e "\nTesting Customer Portal at /:"
curl -s http://$SERVER_HOST/ | head -5

echo -e "\n${GREEN}✅ Deployment fix completed!${NC}"
