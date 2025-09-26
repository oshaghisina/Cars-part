#!/bin/bash
cd /opt/china-car-parts-blue

echo "🔍 Checking git status..."
git status

echo "📝 Adding all changes..."
git add .

echo "💾 Committing changes..."
git commit -m "Fix admin panel production deployment

- Fixed nginx configuration to proxy API requests
- Rebuilt admin panel with correct production API URL
- Fixed database schema with missing SMS columns
- Created admin user for login testing
- Resolved CORS and API connectivity issues"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Push completed!"
