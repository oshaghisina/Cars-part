#!/bin/bash

# Chinese Auto Parts Price Bot - Development Runner
# This script starts the development environment

set -e

echo "🚀 Starting Chinese Auto Parts Price Bot Development Environment"
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

# Copy environment file if it doesn't exist
if [ ! -f "env/.env" ]; then
    echo "⚙️  Creating environment file..."
    cp env/env.example env/.env
    echo "⚠️  Please edit env/.env with your configuration before continuing!"
    echo "   Especially set your TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Load environment variables
export $(cat env/.env | grep -v '^#' | xargs)

# Check if database exists, if not create initial migration
if [ ! -f "data/app.db" ]; then
    echo "🗄️  Initializing database..."
    alembic upgrade head || echo "⚠️  Database migration failed - will create on first run"
fi

echo ""
echo "🎯 Development Environment Ready!"
echo ""
echo "To start the services:"
echo "  Terminal 1 (Backend API):"
echo "    uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  Terminal 2 (Telegram Bot):"
echo "    python -m app.bot.bot"
echo ""
echo "  Terminal 3 (Frontend Panel - Optional):"
echo "    cd app/frontend/panel && npm install && npm run dev"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "🎨 Admin Panel: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop this script"
echo ""

# Keep script running to show status
while true; do
    sleep 60
    echo "⏰ Development environment still running... $(date)"
done
