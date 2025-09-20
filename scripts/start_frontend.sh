#!/bin/bash

# Start frontend development server

set -e

echo "🎨 Starting Frontend Development Server"

# Navigate to frontend directory
cd app/frontend/panel

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start development server
echo "🌐 Starting frontend server on http://localhost:5173"
npm run dev
