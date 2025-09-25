#!/bin/bash

# Stop All Servers Script
# This script stops all running servers for the China Car Parts application

echo "🛑 Stopping China Car Parts Application Servers..."
echo "=================================================="

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "🔪 Stopping $service_name on port $port..."
        PID=$(lsof -ti :$port)
        if [ ! -z "$PID" ]; then
            kill $PID
            sleep 2
            
            # Force kill if still running
            if lsof -i :$port >/dev/null 2>&1; then
                echo "💀 Force killing $service_name on port $port"
                kill -9 $PID
            fi
        fi
        echo "✅ $service_name stopped"
    else
        echo "ℹ️  $service_name not running on port $port"
    fi
}

# Stop all servers
kill_port 8001 "Backend API"
kill_port 5173 "Admin Panel"
kill_port 5174 "Web Portal"
kill_port 5175 "Admin Panel (backup)"

echo ""
echo "✅ All servers stopped successfully!"
echo "=================================================="
