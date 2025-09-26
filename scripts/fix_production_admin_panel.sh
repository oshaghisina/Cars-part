#!/bin/bash

# Quick fix helper for adjusting the admin panel API base URL in production.

set -euo pipefail

echo "🔧 Fixing Production Admin Panel API Configuration..."
echo "=================================================="

if [ -n "${PROD_HOST:-}" ] && hostname -I | grep -q "$PROD_HOST"; then
  echo "✅ Running on production server"
else
  echo "⚠️ This script is intended for the production server"
  echo "   Current server: $(hostname -I)"
fi

cd /path/to/your/project  # Update this path before using the script

echo "🔧 Method 1: Updating built files..."
if [ -d "app/frontend/panel/dist" ]; then
  find app/frontend/panel/dist -name "*.js" -exec sed -i 's|http://localhost:8001/api/v1|/api/v1|g' {} \;
  echo "✅ Updated built files"
else
  echo "❌ Build directory not found. Run the build first."
fi

echo "🔧 Method 2: Rebuilding with production config..."
cd app/frontend/panel
export VITE_API_BASE_URL="/api/v1"
npm run build:panel

if [ $? -eq 0 ]; then
  echo "✅ Admin panel rebuilt successfully!"
  echo "🌐 Admin panel will now connect to: /api/v1"
else
  echo "❌ Rebuild failed!"
fi

echo
echo "🎯 Next steps:"
echo "1. Restart your web server to serve the updated admin panel"
echo "2. Test login at your production panel URL"
echo "3. Verify API calls go to: /api/v1"
