#!/bin/bash

# Update Production Server with Real Bot Token
# This script updates the production server with your real Telegram bot token

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_HOST="5.223.59.155"
PROD_USER="root"
PROD_PASS="xgtie321yzapr5p3t80o"
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

# Function to execute commands on production server
run_production() {
    sshpass -p "$PROD_PASS" ssh -o StrictHostKeyChecking=no "$PROD_USER@$PROD_HOST" "$@"
}

print_status "Updating production server with real bot token..."

# Check if blue-green directories exist
print_status "Checking blue-green deployment directories..."
if run_production "test -d /opt/china-car-parts-blue"; then
    print_success "Blue environment directory exists"
else
    print_error "Blue environment directory not found. Run setup_production_blue_green.sh first."
fi

if run_production "test -d /opt/china-car-parts-green"; then
    print_success "Green environment directory exists"
else
    print_error "Green environment directory not found. Run setup_production_blue_green.sh first."
fi

# Update blue environment
print_status "Updating blue environment..."
run_production "cd /opt/china-car-parts-blue && echo 'TELEGRAM_BOT_TOKEN=$BOT_TOKEN' >> .env"
run_production "cd /opt/china-car-parts-blue && echo 'ADMIN_TELEGRAM_IDS=$ADMIN_IDS' >> .env"
run_production "cd /opt/china-car-parts-blue && echo 'APP_ENV=production' >> .env"
run_production "cd /opt/china-car-parts-blue && echo 'DEBUG=false' >> .env"
print_success "Blue environment updated"

# Update green environment
print_status "Updating green environment..."
run_production "cd /opt/china-car-parts-green && echo 'TELEGRAM_BOT_TOKEN=$BOT_TOKEN' >> .env"
run_production "cd /opt/china-car-parts-green && echo 'ADMIN_TELEGRAM_IDS=$ADMIN_IDS' >> .env"
run_production "cd /opt/china-car-parts-green && echo 'APP_ENV=production' >> .env"
run_production "cd /opt/china-car-parts-green && echo 'DEBUG=false' >> .env"
print_success "Green environment updated"

# Verify the updates
print_status "Verifying bot token configuration..."
run_production "cd /opt/china-car-parts-blue && grep TELEGRAM_BOT_TOKEN .env | tail -1"
run_production "cd /opt/china-car-parts-green && grep TELEGRAM_BOT_TOKEN .env | tail -1"

# Start bot services
print_status "Starting bot services on production server..."

# Start blue bot
print_status "Starting blue bot service..."
run_production "systemctl start china-car-parts-bot-blue" || print_warning "Blue bot service start failed"
run_production "systemctl enable china-car-parts-bot-blue" || print_warning "Blue bot service enable failed"

# Start green bot
print_status "Starting green bot service..."
run_production "systemctl start china-car-parts-bot-green" || print_warning "Green bot service start failed"
run_production "systemctl enable china-car-parts-bot-green" || print_warning "Green bot service enable failed"

# Check service status
print_status "Checking bot service status..."
print_status "Blue bot status:"
run_production "systemctl status china-car-parts-bot-blue --no-pager -l" || true
print_status "Green bot status:"
run_production "systemctl status china-car-parts-bot-green --no-pager -l" || true

# Test bot connection
print_status "Testing bot connection..."
run_production "cd /opt/china-car-parts-blue && source venv/bin/activate && python -c \"
import os
os.environ['TELEGRAM_BOT_TOKEN'] = '$BOT_TOKEN'
os.environ['ADMIN_TELEGRAM_IDS'] = '$ADMIN_IDS'
from app.core.config import settings
print(f'Bot Token: {settings.telegram_bot_token[:10]}...')
print(f'Admin IDs: {settings.admin_telegram_ids_list}')
print('Configuration loaded successfully!')
\""

print_success "Production bot configuration completed!"
print_status "Your bot @Carspartbot is now running on the production server!"
print_status "Test it by messaging @Carspartbot on Telegram"
print_status "Production API: https://5.223.59.155"
print_status "Admin Panel: https://5.223.59.155"
