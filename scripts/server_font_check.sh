#!/bin/bash

echo "🔍 Checking Persian Font Deployment on Server"
echo "=============================================="

# Check if font files exist in the deployment directory
echo "📁 Checking font files in deployment directory..."
if [ -d "/opt/china-car-parts/app/frontend/web/dist/assets" ]; then
    echo "✅ Web dist directory exists"
    ls -la /opt/china-car-parts/app/frontend/web/dist/assets/ | grep -i peyda
    echo ""
    
    # Check if CSS contains font references
    echo "📄 Checking CSS for font references..."
    if [ -f "/opt/china-car-parts/app/frontend/web/dist/assets/index-"*.css ]; then
        CSS_FILE=$(ls /opt/china-car-parts/app/frontend/web/dist/assets/index-*.css | head -1)
        echo "CSS file: $CSS_FILE"
        if grep -q "Peyda" "$CSS_FILE"; then
            echo "✅ CSS contains Peyda font references"
        else
            echo "❌ CSS missing Peyda font references"
        fi
    else
        echo "❌ CSS file not found"
    fi
else
    echo "❌ Web dist directory not found"
fi

echo ""
echo "🌐 Checking Nginx configuration..."
if [ -f "/etc/nginx/sites-available/china-car-parts" ]; then
    echo "✅ Nginx config exists"
    if grep -q "font/woff" /etc/nginx/sites-available/china-car-parts; then
        echo "✅ Nginx has font MIME type configuration"
    else
        echo "❌ Nginx missing font MIME type configuration"
    fi
else
    echo "❌ Nginx config not found"
fi

echo ""
echo "🔄 Checking Nginx status..."
systemctl status nginx --no-pager -l | head -10

echo ""
echo "📊 Checking recent Nginx logs for font requests..."
tail -20 /var/log/nginx/china-car-parts.access.log | grep -i "woff\|font" || echo "No font requests found in recent logs"

echo ""
echo "🔧 Suggested fixes if fonts are not working:"
echo "1. Reload Nginx: sudo systemctl reload nginx"
echo "2. Check file permissions: sudo chmod -R 755 /opt/china-car-parts/app/frontend/web/dist/"
echo "3. Clear browser cache and hard refresh (Ctrl+F5)"
echo "4. Check browser console for font loading errors"
