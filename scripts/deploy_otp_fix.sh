#!/bin/bash
# OTP Production Fix Deployment Script
# This script deploys the OTP fix to production

set -e  # Exit on any error

echo "🚀 Deploying OTP Fix to Production"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app/api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 Step 1: Creating OTP tables..."
python scripts/create_otp_tables_production.py

if [ $? -eq 0 ]; then
    echo "✅ Database tables created successfully"
else
    echo "❌ Failed to create database tables"
    exit 1
fi

echo ""
echo "📋 Step 2: Testing OTP functionality..."
python test_otp_production.py

if [ $? -eq 0 ]; then
    echo "✅ OTP functionality test passed"
else
    echo "❌ OTP functionality test failed"
    exit 1
fi

echo ""
echo "📋 Step 3: Testing API endpoints..."

# Test health check
echo "🔍 Testing health check endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/otp/health || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ Health check endpoint working"
else
    echo "⚠️  Health check endpoint returned: $HEALTH_RESPONSE"
    echo "   (This is expected if the server isn't running)"
fi

echo ""
echo "🎉 OTP Fix Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Start your production server"
echo "2. Test the OTP endpoint:"
echo "   curl -X POST http://your-server/api/v1/otp/phone/login/request \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"phone_number\": \"+989123456789\"}'"
echo ""
echo "3. Check health status:"
echo "   curl -X GET http://your-server/api/v1/otp/health"
echo ""
echo "✅ The OTP SMS issue should now be resolved!"
