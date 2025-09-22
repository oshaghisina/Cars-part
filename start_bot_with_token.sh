#!/bin/bash

# Start Telegram Bot with Real Token
# This script sets up the environment and starts the bot with your real token

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/sinaoshaghi/Projects/China Car Parts"
BOT_TOKEN="8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4"
ADMIN_IDS="176007160"

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
    exit 1
}

# Change to project directory
cd "$PROJECT_DIR" || print_error "Failed to change to project directory"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate || print_error "Failed to activate virtual environment"

# Set environment variables
print_status "Setting environment variables..."
export TELEGRAM_BOT_TOKEN="$BOT_TOKEN"
export ADMIN_TELEGRAM_IDS="$ADMIN_IDS"
export APP_ENV="development"
export DEBUG="true"
export DATABASE_URL="sqlite:///./data/app.db"
export HOST="0.0.0.0"
export PORT="8001"
export FRONTEND_ORIGIN="http://localhost:5173,http://127.0.0.1:5173"

print_success "Environment variables set:"
echo "  TELEGRAM_BOT_TOKEN: ${BOT_TOKEN:0:10}..."
echo "  ADMIN_TELEGRAM_IDS: $ADMIN_IDS"
echo "  APP_ENV: development"
echo "  DATABASE_URL: sqlite:///./data/app.db"

# Start the bot
print_status "Starting Telegram bot with real token..."
python -m app.bot.bot
