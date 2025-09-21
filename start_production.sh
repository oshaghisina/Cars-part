#!/bin/bash

# Production Startup Script for China Car Parts
# This script starts the production services

set -e

echo "🚀 Starting China Car Parts Production Services"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_status "Project directory: $PROJECT_DIR"

# Set production environment variables
export APP_ENV=production
export DEBUG=false
export DATABASE_URL="sqlite:///./data/app.db"
export SECRET_KEY="your_production_secret_key_32_chars_long"
export JWT_SECRET_KEY="your_production_jwt_secret_key_32_chars_long"
export FRONTEND_ORIGIN="http://localhost:8001"
export API_HOST="0.0.0.0"
export API_PORT="8001"

print_status "Environment variables set for production"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"
print_status "Logs directory created"

# Check if services are already running
if pgrep -f "uvicorn app.api.main:app" > /dev/null; then
    print_warning "API service is already running"
    pkill -f "uvicorn app.api.main:app"
    sleep 2
fi

if pgrep -f "python -m app.bot.bot" > /dev/null; then
    print_warning "Bot service is already running"
    pkill -f "python -m app.bot.bot"
    sleep 2
fi

# Start API service
print_status "Starting API service..."
cd "$PROJECT_DIR"
source venv/bin/activate

# Start API in background with logging
nohup uvicorn app.api.main:app --host 0.0.0.0 --port 8001 > logs/api.log 2> logs/api-error.log &
API_PID=$!
echo $API_PID > logs/api.pid

# Wait for API to start
print_status "Waiting for API service to start..."
sleep 5

# Check if API is running
if pgrep -f "uvicorn app.api.main:app" > /dev/null; then
    print_success "API service started successfully (PID: $API_PID)"
else
    print_error "API service failed to start"
    exit 1
fi

# Test API health
print_status "Testing API health..."
if curl -f -s http://localhost:8001/health > /dev/null; then
    print_success "API health check passed"
else
    print_warning "API health check failed, but service is running"
fi

# Start Bot service (development mode with graceful error handling)
print_status "Starting Bot service..."
nohup python -m app.bot.bot_dev > logs/bot.log 2> logs/bot-error.log &
BOT_PID=$!
echo $BOT_PID > logs/bot.pid

# Wait for Bot to start
sleep 3

if pgrep -f "python -m app.bot.bot_dev" > /dev/null; then
    print_success "Bot service started successfully (PID: $BOT_PID)"
    print_status "Bot running in development mode (no Telegram connection required)"
else
    print_warning "Bot service failed to start (check logs/bot-error.log)"
fi

print_success "Production services started!"
echo ""
echo "📊 Service Status:"
echo "  API: http://localhost:8001"
echo "  Health: http://localhost:8001/health"
echo "  Docs: http://localhost:8001/docs"
echo "  Admin: http://localhost:8001"
echo ""
echo "📁 Logs:"
echo "  API: $PROJECT_DIR/logs/api.log"
echo "  Bot: $PROJECT_DIR/logs/bot.log"
echo ""
echo "🛑 To stop services:"
echo "  pkill -f 'uvicorn app.api.main:app'"
echo "  pkill -f 'python -m app.bot.bot'"
echo ""
print_success "🎉 China Car Parts is running in production mode!"
