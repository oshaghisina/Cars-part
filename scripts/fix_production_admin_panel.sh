#!/bin/bash

# Quick Fix for Production Admin Panel API Configuration
# This script can be run on the production server to fix the API URL issue

echo "🔧 Fixing Production Admin Panel API Configuration..."
echo "=================================================="

# Check if we're on the production server
if [ "$(hostname -I | grep -o '5\.223\.59\.155')" = "5.223.59.155" ]; then
    echo "✅ Running on production server"
else
    echo "⚠️  This script is designed for production server (5.223.59.155)"
    echo "   Current server: $(hostname -I)"
fi

# Navigate to project directory
cd /path/to/your/project  # Update this path

# Method 1: Update the built admin panel files directly
echo "🔧 Method 1: Updating built files..."
if [ -d "app/frontend/panel/dist" ]; then
    # Find and replace localhost:8001 with production API URL in built files
    find app/frontend/panel/dist -name "*.js" -exec sed -i 's|http://localhost:8001/api/v1|http://5.223.59.155/api/v1|g' {} \;
    echo "✅ Updated built files"
else
    echo "❌ Build directory not found. Run build script first."
fi

# Method 2: Rebuild with correct environment
echo "🔧 Method 2: Rebuilding with production config..."
cd app/frontend/panel
export VITE_API_BASE_URL="http://5.223.59.155/api/v1"
npm run build:panel

if [ $? -eq 0 ]; then
    echo "✅ Admin panel rebuilt successfully!"
    echo "🌐 Admin panel will now connect to: http://5.223.59.155/api/v1"
else
    echo "❌ Rebuild failed!"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Restart your web server to serve the updated admin panel"
echo "2. Test login at: http://5.223.59.155/panel/"
echo "3. Verify API calls go to: http://5.223.59.155/api/v1"
