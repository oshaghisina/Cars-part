#!/bin/bash

# 🚀 Local Staging Deployment Script
# This script creates a local staging environment for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_DIR="/tmp/china-car-parts-staging"
STAGING_PORT=8002
API_PORT=8002
BOT_PORT=8003
LOG_FILE="/tmp/china-car-parts-staging-deploy.log"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a $LOG_FILE
}

# Cleanup function
cleanup() {
    log "🧹 Cleaning up staging environment..."
    pkill -f "uvicorn.*8002" || true
    pkill -f "python.*bot.*staging" || true
    rm -rf "$STAGING_DIR" || true
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if port is available
    if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null; then
        warning "Port $API_PORT is in use, stopping existing services..."
        pkill -f "uvicorn.*8002" || true
        sleep 2
    fi
    
    # Check if staging directory exists and clean it
    if [ -d "$STAGING_DIR" ]; then
        log "🧹 Cleaning existing staging directory..."
        rm -rf "$STAGING_DIR"
    fi
    
    success "Pre-deployment checks passed"
}

# Create staging environment
create_staging_environment() {
    log "🏗️ Creating staging environment..."
    
    # Create staging directory
    mkdir -p "$STAGING_DIR"
    cd "$STAGING_DIR"
    
    # Copy current project to staging
    log "📁 Copying project files to staging..."
    cp -r "/Users/sinaoshaghi/Projects/China Car Parts"/* "$STAGING_DIR/"
    
    # Create staging-specific environment
    log "⚙️ Configuring staging environment..."
    cat > "$STAGING_DIR/.env" << EOF
# Staging Environment Configuration
app_env=staging
debug=false
log_level=INFO

# Database Configuration (separate staging database)
database_url=sqlite:///./data/staging.db

# Telegram Bot Configuration
telegram_bot_token=CHANGEME_YOUR_STAGING_BOT_TOKEN
admin_telegram_ids=176007160

# FastAPI Configuration
secret_key=staging_secret_key_32_chars_long
jwt_secret_key=staging_jwt_secret_key_32_chars_long
jwt_algorithm=HS256
jwt_access_token_expire_minutes=1440

# Frontend Configuration
frontend_origin=http://localhost:$API_PORT,http://127.0.0.1:$API_PORT

# Server Configuration
host=0.0.0.0
port=$API_PORT

# AI Configuration
ai_enabled=true
openai_api_key=CHANGEME_YOUR_OPENAI_API_KEY
openai_model=gpt-3.5-turbo
openai_embedding_model=text-embedding-3-small
openai_max_tokens=1000
openai_temperature=0.3

# Rate Limiting
rate_limit_per_minute=1000
rate_limit_burst=100

# Logging
log_file=logs/staging.log

# Admin Panel
admin_panel_enabled=true
admin_panel_port=3001

# Features
bulk_limit_default=10
maintenance_mode=false

# Redis
redis_url=redis://localhost:6379/1
EOF

    success "Staging environment created"
}

# Set up Python environment
setup_python_environment() {
    log "🐍 Setting up Python environment..."
    
    cd "$STAGING_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    success "Python environment set up"
}

# Run database migrations
run_database_migrations() {
    log "🗄️ Running database migrations..."
    
    cd "$STAGING_DIR"
    source venv/bin/activate
    
    # Create data directory
    mkdir -p data
    
    # Run migrations
    alembic upgrade head
    
    # Create sample data
    python create_sample_data.py
    
    success "Database migrations completed"
}

# Start staging services
start_staging_services() {
    log "🚀 Starting staging services..."
    
    cd "$STAGING_DIR"
    source venv/bin/activate
    
    # Start API service
    log "🌐 Starting API service on port $API_PORT..."
    nohup uvicorn app.api.main:app --host 0.0.0.0 --port $API_PORT > logs/api-staging.log 2> logs/api-staging-error.log &
    API_PID=$!
    echo $API_PID > logs/api-staging.pid
    
    # Wait for API to start
    sleep 5
    
    # Test API health
    if curl -f -s "http://localhost:$API_PORT/health" > /dev/null; then
        success "API service started successfully (PID: $API_PID)"
    else
        error "API service failed to start"
    fi
    
    # Start Bot service
    log "🤖 Starting Bot service..."
    nohup python -m app.bot.bot_dev > logs/bot-staging.log 2> logs/bot-staging-error.log &
    BOT_PID=$!
    echo $BOT_PID > logs/bot-staging.pid
    
    # Wait for Bot to start
    sleep 3
    
    if pgrep -f "python -m app.bot.bot_dev" > /dev/null; then
        success "Bot service started successfully (PID: $BOT_PID)"
    else
        warning "Bot service failed to start (check logs/bot-staging-error.log)"
    fi
}

# Run staging tests
run_staging_tests() {
    log "🧪 Running staging tests..."
    
    cd "$STAGING_DIR"
    source venv/bin/activate
    
    # Update test URL for staging
    sed "s|http://localhost:8001|http://localhost:$API_PORT|g" test_production_setup.py > test_staging_setup.py
    
    # Run tests
    python test_staging_setup.py
    
    success "Staging tests completed"
}

# Show staging status
show_staging_status() {
    log "📊 Staging Environment Status"
    echo "================================"
    echo ""
    echo "📍 Staging Directory: $STAGING_DIR"
    echo "📍 API Port: $API_PORT"
    echo "📍 Bot Port: $BOT_PORT"
    echo ""
    echo "🌐 Access Points:"
    echo "  API: http://localhost:$API_PORT"
    echo "  Health: http://localhost:$API_PORT/health"
    echo "  Docs: http://localhost:$API_PORT/docs"
    echo "  Admin: http://localhost:$API_PORT"
    echo ""
    echo "📁 Logs:"
    echo "  API: $STAGING_DIR/logs/api-staging.log"
    echo "  Bot: $STAGING_DIR/logs/bot-staging.log"
    echo ""
    echo "🛑 To stop staging services:"
    echo "  pkill -f 'uvicorn.*8002'"
    echo "  pkill -f 'python.*bot.*staging'"
    echo "  rm -rf $STAGING_DIR"
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting Local Staging Deployment"
    echo "=================================="
    
    # Set up trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    pre_deployment_checks
    create_staging_environment
    setup_python_environment
    run_database_migrations
    start_staging_services
    run_staging_tests
    show_staging_status
    
    success "🎉 Staging deployment completed successfully!"
    echo ""
    echo "Your staging environment is now running at:"
    echo "🌐 http://localhost:$API_PORT"
    echo ""
    echo "This simulates a real staging server deployment!"
}

# Run main function
main "$@"
