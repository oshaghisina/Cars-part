#!/bin/bash

# Admin Panel Startup Script
# This script ensures only one admin panel server is running

echo "🚀 Starting Admin Panel Server..."

# Check if port 5173 is already in use
if lsof -i :5173 >/dev/null 2>&1; then
    echo "⚠️  Port 5173 is already in use. Killing existing process..."
    
    # Find and kill the process using port 5173
    PID=$(lsof -ti :5173)
    if [ ! -z "$PID" ]; then
        echo "🔪 Killing process $PID on port 5173"
        kill $PID
        sleep 2
        
        # Force kill if still running
        if lsof -i :5173 >/dev/null 2>&1; then
            echo "💀 Force killing process on port 5173"
            kill -9 $PID
            sleep 1
        fi
    fi
fi

# Check if port 5175 is already in use (backup port)
if lsof -i :5175 >/dev/null 2>&1; then
    echo "⚠️  Port 5175 is already in use. Killing existing process..."
    
    # Find and kill the process using port 5175
    PID=$(lsof -ti :5175)
    if [ ! -z "$PID" ]; then
        echo "🔪 Killing process $PID on port 5175"
        kill $PID
        sleep 2
        
        # Force kill if still running
        if lsof -i :5175 >/dev/null 2>&1; then
            echo "💀 Force killing process on port 5175"
            kill -9 $PID
            sleep 1
        fi
    fi
fi

# Navigate to admin panel directory
cd "/Users/sinaoshaghi/Projects/China Car Parts/app/frontend/panel"

echo "📁 Starting admin panel from: $(pwd)"
echo "🌐 Admin panel will be available at: http://localhost:5173"
echo ""

# Start the admin panel server
npm run dev
