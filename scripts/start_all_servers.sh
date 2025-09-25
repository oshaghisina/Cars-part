#!/bin/bash

# Master Server Startup Script
# This script starts all servers for the China Car Parts application

echo "🚀 Starting China Car Parts Application Servers..."
echo "=================================================="

# Function to check if a port is in use and kill the process
kill_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. Killing existing process..."
        PID=$(lsof -ti :$port)
        if [ ! -z "$PID" ]; then
            echo "🔪 Killing process $PID on port $port"
            kill $PID
            sleep 2
            
            # Force kill if still running
            if lsof -i :$port >/dev/null 2>&1; then
                echo "💀 Force killing process on port $port"
                kill -9 $PID
                sleep 1
            fi
        fi
    fi
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
kill_port 8001  # Backend API
kill_port 5173  # Admin Panel
kill_port 5174  # Web Portal
kill_port 5175  # Admin Panel (backup port)

echo ""
echo "🔧 Starting Backend API Server..."
cd "/Users/sinaoshaghi/Projects/China Car Parts"
source venv/bin/activate
MELIPAYAMAK_USERNAME="9335540052" \
MELIPAYAMAK_PASSWORD="59a3a4a7-b8fe-422c-be38-e07ebec590c6" \
SMS_SENDER_NUMBER="50002710040052" \
SMS_ENABLED="true" \
TELEGRAM_BOT_TOKEN="8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4" \
TELEGRAM_BOT_USERNAME="ChinaCarPartBot" \
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8001 --reload &

# Wait a moment for the backend to start
sleep 3

echo "🎨 Starting Admin Panel Server..."
cd "/Users/sinaoshaghi/Projects/China Car Parts/app/frontend/panel"
npm run dev &

# Wait a moment for the admin panel to start
sleep 3

echo "🌐 Starting Web Portal Server..."
cd "/Users/sinaoshaghi/Projects/China Car Parts/app/frontend/web"
npm run dev &

echo ""
echo "✅ All servers started successfully!"
echo "=================================================="
echo "🔧 Backend API:     http://localhost:8001"
echo "🎨 Admin Panel:     http://localhost:5173"
echo "🌐 Web Portal:      http://localhost:5174"
echo "📚 API Docs:        http://localhost:8001/docs"
echo "=================================================="
echo ""
echo "💡 To stop all servers, press Ctrl+C or run: ./scripts/stop_all_servers.sh"
echo ""

# Wait for user input to keep the script running
read -p "Press Enter to stop all servers..."
