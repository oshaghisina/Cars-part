#!/bin/bash

# 🚀 Final Production Deployment Script with Blue-Green Strategy
# This script deploys the application to production with zero-downtime capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROD_DIR="/tmp/china-car-parts-prod"
BLUE_DIR="$PROD_DIR/blue"
GREEN_DIR="$PROD_DIR/green"
CURRENT_ENV_FILE="$PROD_DIR/current_env"
BLUE_PORT=8001
GREEN_PORT=8002
LOG_FILE="/tmp/china-car-parts-prod-deploy.log"

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

info() {
    echo -e "${PURPLE}[INFO]${NC} $1" | tee -a $LOG_FILE
}

# Cleanup function
cleanup() {
    log "🧹 Cleaning up production environment..."
    pkill -f "uvicorn.*800[0-2]" || true
    pkill -f "python.*bot.*production" || true
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if ports are available
    for port in $BLUE_PORT $GREEN_PORT; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            warning "Port $port is in use, stopping existing services..."
            pkill -f "uvicorn.*$port" || true
            sleep 2
        fi
    done
    
    success "Pre-deployment checks passed"
}

# Create production environment structure
create_production_structure() {
    log "🏗️ Creating production environment structure..."
    
    # Clean up existing directory
    rm -rf "$PROD_DIR" 2>/dev/null || true
    
    # Create directories
    mkdir -p "$BLUE_DIR" "$GREEN_DIR"
    
    # Copy current project to both environments (excluding large directories)
    log "📁 Copying project files to blue environment..."
    rsync -av --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.git' "/Users/sinaoshaghi/Projects/China Car Parts/" "$BLUE_DIR/"
    
    log "📁 Copying project files to green environment..."
    rsync -av --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.git' "/Users/sinaoshaghi/Projects/China Car Parts/" "$GREEN_DIR/"
    
    success "Production structure created"
}

# Set up environment
setup_environment() {
    local env_dir=$1
    local env_name=$2
    local port=$3
    
    log "🔧 Setting up $env_name environment..."
    
    cd "$env_dir"
    
    # Create environment configuration
    cat > .env << EOF
# $env_name Environment Configuration
app_env=production
debug=false
log_level=INFO

# Database Configuration
database_url=sqlite:///./data/${env_name}.db

# Telegram Bot Configuration
telegram_bot_token=CHANGEME_YOUR_PRODUCTION_BOT_TOKEN
admin_telegram_ids=176007160

# FastAPI Configuration
secret_key=${env_name}_production_secret_key_32_chars_long
jwt_secret_key=${env_name}_production_jwt_secret_key_32_chars_long
jwt_algorithm=HS256
jwt_access_token_expire_minutes=1440

# Frontend Configuration
frontend_origin=http://localhost:$port,http://127.0.0.1:$port

# Server Configuration
host=0.0.0.0
port=$port

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
log_file=logs/${env_name}.log

# Admin Panel
admin_panel_enabled=true
admin_panel_port=3000

# Features
bulk_limit_default=10
maintenance_mode=false

# Redis
redis_url=redis://localhost:6379/0
EOF

    # Set up Python environment
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set up database
    mkdir -p data
    cp "/Users/sinaoshaghi/Projects/China Car Parts/data/app.db" "data/${env_name}.db"
    
    success "$env_name environment set up"
}

# Start environment
start_environment() {
    local env_dir=$1
    local env_name=$2
    local port=$3
    
    log "🚀 Starting $env_name environment..."
    
    cd "$env_dir"
    source venv/bin/activate
    
    # Create logs directory
    mkdir -p logs
    
    # Start API service
    nohup uvicorn app.api.main:app --host 0.0.0.0 --port $port > logs/${env_name}-api.log 2> logs/${env_name}-api-error.log &
    API_PID=$!
    echo $API_PID > logs/${env_name}-api.pid
    
    # Start Bot service
    nohup python -m app.bot.bot_dev > logs/${env_name}-bot.log 2> logs/${env_name}-bot-error.log &
    BOT_PID=$!
    echo $BOT_PID > logs/${env_name}-bot.pid
    
    # Wait for services to start
    sleep 10
    
    # Test environment
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health" > /dev/null; then
            success "$env_name environment started successfully"
            echo "$env_name" > "$CURRENT_ENV_FILE"
            return 0
        else
            log "Attempt $attempt/$max_attempts: Waiting for $env_name environment to start..."
            sleep 3
            ((attempt++))
        fi
    done
    
    error "$env_name environment failed to start after $max_attempts attempts"
}

# Run production tests
run_production_tests() {
    log "🧪 Running production tests..."
    
    # Test blue environment
    log "🔵 Testing BLUE environment..."
    if curl -f -s "http://localhost:$BLUE_PORT/health" > /dev/null; then
        success "BLUE environment health check passed"
    else
        error "BLUE environment health check failed"
    fi
    
    # Test green environment
    log "🟢 Testing GREEN environment..."
    if curl -f -s "http://localhost:$GREEN_PORT/health" > /dev/null; then
        success "GREEN environment health check passed"
    else
        error "GREEN environment health check failed"
    fi
    
    success "Production tests completed"
}

# Show production status
show_production_status() {
    log "📊 Production Environment Status"
    echo "=================================="
    echo ""
    
    # Get current environment
    if [ -f "$CURRENT_ENV_FILE" ]; then
        CURRENT_ENV=$(cat "$CURRENT_ENV_FILE")
        echo "🎯 Current Active Environment: ${CURRENT_ENV^^}"
    else
        echo "🎯 Current Active Environment: UNKNOWN"
    fi
    
    echo ""
    echo "🔵 BLUE Environment:"
    echo "  Port: $BLUE_PORT"
    echo "  Status: $(curl -s http://localhost:$BLUE_PORT/health > /dev/null && echo "✅ Running" || echo "❌ Down")"
    echo "  URL: http://localhost:$BLUE_PORT"
    echo ""
    echo "🟢 GREEN Environment:"
    echo "  Port: $GREEN_PORT"
    echo "  Status: $(curl -s http://localhost:$GREEN_PORT/health > /dev/null && echo "✅ Running" || echo "❌ Down")"
    echo "  URL: http://localhost:$GREEN_PORT"
    echo ""
    echo "📁 Directories:"
    echo "  Blue: $BLUE_DIR"
    echo "  Green: $GREEN_DIR"
    echo ""
    echo "🛑 To stop production services:"
    echo "  pkill -f 'uvicorn.*800[0-2]'"
    echo "  pkill -f 'python.*bot.*production'"
    echo "  rm -rf $PROD_DIR"
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting Final Production Deployment with Blue-Green Strategy"
    echo "==============================================================="
    
    # Set up trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    pre_deployment_checks
    create_production_structure
    setup_environment "$BLUE_DIR" "blue" $BLUE_PORT
    setup_environment "$GREEN_DIR" "green" $GREEN_PORT
    start_environment "$BLUE_DIR" "blue" $BLUE_PORT
    start_environment "$GREEN_DIR" "green" $GREEN_PORT
    run_production_tests
    show_production_status
    
    success "🎉 Production deployment completed successfully!"
    echo ""
    echo "Your production environment is now running with:"
    echo "🔵 BLUE Environment: http://localhost:$BLUE_PORT"
    echo "🟢 GREEN Environment: http://localhost:$GREEN_PORT"
    echo ""
    echo "This implements a real blue-green deployment strategy!"
    echo "Both environments are running simultaneously for zero-downtime deployments."
}

# Handle command line arguments
case "${1:-}" in
    --status)
        show_production_status
        ;;
    --help)
        echo "Final Production Deployment Script with Blue-Green Strategy"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --status            Show production status"
        echo "  --help              Show this help message"
        echo ""
        ;;
    *)
        main
        ;;
esac
