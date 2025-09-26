#!/bin/bash

# Helper to redeploy the admin panel with the correct API base URL.

set -euo pipefail

echo "🚀 Deploying Admin Panel Fix"
echo "============================"

PROJECT_DIR="/root/China-Car-Parts"  # Update with actual path before running

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Project directory not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "📥 Pulling latest code..."
git pull origin main

echo "📁 Building admin panel..."
cd app/frontend/panel
npm install
export VITE_API_BASE_URL="/api/v1"
npm run build:panel

echo "🔍 Ensuring no localhost references remain..."
find dist -name "*.js" -exec sed -i 's|http://localhost:8001/api/v1|/api/v1|g' {} \;

echo "🌐 Restarting nginx..."
sudo systemctl restart nginx

echo "✅ Done. Verify the panel at your production URL."
