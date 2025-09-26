#!/bin/bash

# Build Admin Panel for Production Deployment
# This script sets the correct API URL and builds the admin panel

echo "🏗️  Building Admin Panel for Production..."
echo "=================================================="

# Navigate to admin panel directory
cd app/frontend/panel

# Set production environment variable
export VITE_API_BASE_URL="/api/v1"

echo "🔧 Setting API Base URL: $VITE_API_BASE_URL"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build for production
echo "🏗️  Building admin panel..."
npm run build:panel

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Admin panel built successfully!"
    echo "📁 Build output: app/frontend/panel/dist/"
    echo ""
    echo "🚀 Deployment instructions:"
    echo "1. Copy the contents of app/frontend/panel/dist/ to your web server"
    echo "2. Ensure the admin panel is served from /panel/ path"
    echo "3. The admin panel will now connect to: $VITE_API_BASE_URL"
else
    echo "❌ Build failed!"
    exit 1
fi
