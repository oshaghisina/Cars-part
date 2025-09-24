#!/bin/bash

echo "🚀 Deploying Persian Font Fix to Server"
echo "======================================="

# Check if we're in the right directory
if [ ! -d "/opt/china-car-parts" ]; then
    echo "❌ Error: /opt/china-car-parts directory not found"
    echo "Please run this script from the server"
    exit 1
fi

cd /opt/china-car-parts

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "🔧 Rebuilding frontend with font fixes..."
cd app/frontend/web
npm install
npm run build

echo "📁 Copying new build to deployment directory..."
cp -r dist/* /opt/china-car-parts/app/frontend/web/dist/

echo "⚙️ Updating Nginx configuration..."
sudo cp deployment/configs/nginx-production.conf /etc/nginx/sites-available/china-car-parts

echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo "🔐 Fixing file permissions..."
sudo chmod -R 755 /opt/china-car-parts/app/frontend/web/dist/

echo "✅ Deployment complete!"
echo ""
echo "🔍 Checking font files..."
ls -la /opt/china-car-parts/app/frontend/web/dist/assets/ | grep -i peyda | head -5

echo ""
echo "🌐 Testing font loading..."
if curl -s -I "http://localhost/assets/PeydaWeb-Regular"* 2>/dev/null | grep -q "200 OK"; then
    echo "✅ Font files are accessible"
else
    echo "⚠️ Font files may not be accessible yet (try hard refresh in browser)"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
echo "2. Check browser console for any font loading errors"
echo "3. Visit your website to see Persian fonts"
