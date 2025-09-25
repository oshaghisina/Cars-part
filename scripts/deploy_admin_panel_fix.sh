#!/bin/bash

# Complete Admin Panel Fix Deployment Script
# Run this script on your production server to fix the API URL issue

echo "🚀 Deploying Admin Panel Fix to Production Server"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're on the production server
echo "🔍 Checking server environment..."
if [ "$(hostname -I | grep -o '5\.223\.59\.155')" = "5.223.59.155" ]; then
    print_status "Running on production server (5.223.59.155)"
else
    print_warning "This script is designed for production server (5.223.59.155)"
    echo "Current server IPs: $(hostname -I)"
fi

# Navigate to project directory (update this path as needed)
PROJECT_DIR="/root/China-Car-Parts"  # Update this to your actual project path
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    echo "Please update PROJECT_DIR variable in this script to your actual project path"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1
print_status "Navigated to project directory: $PROJECT_DIR"

# Step 1: Pull latest changes
echo ""
echo "📥 Pulling latest changes from GitHub..."
git pull origin main
if [ $? -eq 0 ]; then
    print_status "Successfully pulled latest changes"
else
    print_error "Failed to pull changes from GitHub"
    exit 1
fi

# Step 2: Check if admin panel directory exists
ADMIN_PANEL_DIR="app/frontend/panel"
if [ ! -d "$ADMIN_PANEL_DIR" ]; then
    print_error "Admin panel directory not found: $ADMIN_PANEL_DIR"
    exit 1
fi

cd "$ADMIN_PANEL_DIR" || exit 1
print_status "Navigated to admin panel directory"

# Step 3: Install dependencies if needed
echo ""
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found, installing dependencies..."
    npm install
    if [ $? -eq 0 ]; then
        print_status "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
else
    print_status "Dependencies already installed"
fi

# Step 4: Set production environment and rebuild
echo ""
echo "🔧 Setting production environment and rebuilding admin panel..."
export VITE_API_BASE_URL="http://5.223.59.155/api/v1"
print_status "Set VITE_API_BASE_URL to: $VITE_API_BASE_URL"

# Build the admin panel
npm run build:panel
if [ $? -eq 0 ]; then
    print_status "Admin panel built successfully!"
else
    print_error "Failed to build admin panel"
    exit 1
fi

# Step 5: Verify the build contains correct API URL
echo ""
echo "🔍 Verifying build contains correct API URL..."
if grep -r "http://5.223.59.155/api/v1" dist/ > /dev/null; then
    print_status "Build contains correct production API URL"
else
    print_warning "Build may not contain correct API URL, applying manual fix..."
    find dist -name "*.js" -exec sed -i 's|http://localhost:8001/api/v1|http://5.223.59.155/api/v1|g' {} \;
    print_status "Manual fix applied"
fi

# Step 6: Check if web server is running
echo ""
echo "🌐 Checking web server status..."
if systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
    WEB_SERVER="nginx"
elif systemctl is-active --quiet apache2; then
    print_status "Apache2 is running"
    WEB_SERVER="apache2"
else
    print_warning "No web server detected (nginx/apache2)"
    WEB_SERVER="none"
fi

# Step 7: Restart web server if needed
if [ "$WEB_SERVER" != "none" ]; then
    echo ""
    echo "🔄 Restarting web server..."
    sudo systemctl restart "$WEB_SERVER"
    if [ $? -eq 0 ]; then
        print_status "Web server restarted successfully"
    else
        print_error "Failed to restart web server"
    fi
fi

# Step 8: Test the fix
echo ""
echo "🧪 Testing the fix..."
echo "Testing API endpoint: http://5.223.59.155/api/v1/health"
if curl -s http://5.223.59.155/api/v1/health > /dev/null; then
    print_status "API endpoint is accessible"
else
    print_warning "API endpoint may not be accessible"
fi

# Final instructions
echo ""
echo "🎯 Deployment Complete!"
echo "=================================================="
print_status "Admin panel has been updated with production API URL"
print_status "Admin panel URL: http://5.223.59.155/panel/"
print_status "API URL: http://5.223.59.155/api/v1"
echo ""
echo "📋 Next steps:"
echo "1. Visit http://5.223.59.155/panel/ in your browser"
echo "2. Try logging in with admin/adminpassword"
echo "3. Check browser console for any remaining errors"
echo ""
echo "🔧 If you still see CORS errors:"
echo "1. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)"
echo "2. Check that the API server is running on port 8001"
echo "3. Verify CORS settings in your backend configuration"
