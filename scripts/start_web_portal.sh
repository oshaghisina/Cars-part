#!/bin/bash

# Web Portal Startup Script
# This script ensures only one web portal server is running

echo "🚀 Starting Web Portal Server..."

# Check if port 5174 is already in use
if lsof -i :5174 >/dev/null 2>&1; then
    echo "⚠️  Port 5174 is already in use. Killing existing process..."
    
    # Find and kill the process using port 5174
    PID=$(lsof -ti :5174)
    if [ ! -z "$PID" ]; then
        echo "🔪 Killing process $PID on port 5174"
        kill $PID
        sleep 2
        
        # Force kill if still running
        if lsof -i :5174 >/dev/null 2>&1; then
            echo "💀 Force killing process on port 5174"
            kill -9 $PID
            sleep 1
        fi
    fi
fi

# Navigate to web portal directory
cd "/Users/sinaoshaghi/Projects/China Car Parts/app/frontend/web"

echo "📁 Starting web portal from: $(pwd)"
echo "🌐 Web portal will be available at: http://localhost:5174"
echo ""

# Start the web portal server
npm run dev
