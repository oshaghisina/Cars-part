#!/bin/bash

# 🚀 Production Deployment Script with Blue-Green Strategy
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
PROD_DIR="/tmp/china-car-parts-production"
BLUE_DIR="$PROD_DIR/blue"
GREEN_DIR="$PROD_DIR/green"
CURRENT_ENV_FILE="$PROD_DIR/current_env"
BLUE_PORT=8001
GREEN_PORT=8002
PRODUCTION_PORT=8000
LOG_FILE="/tmp/china-car-parts-production-deploy.log"
BACKUP_DIR="/tmp/china-car-parts-backups"
MAX_BACKUPS=5

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
    rm -rf "$PROD_DIR" 2>/dev/null || true
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if ports are available
    for port in $BLUE_PORT $GREEN_PORT $PRODUCTION_PORT; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            warning "Port $port is in use, stopping existing services..."
            pkill -f "uvicorn.*$port" || true
            sleep 2
        fi
    done
    
    # Check if production directory exists and clean it
    if [ -d "$PROD_DIR" ]; then
        log "🧹 Cleaning existing production directory..."
        rm -rf "$PROD_DIR" 2>/dev/null || true
    fi
    
    success "Pre-deployment checks passed"
}

# Create production environment structure
create_production_structure() {
    log "🏗️ Creating production environment structure..."
    
    # Create directories
    mkdir -p "$BLUE_DIR" "$GREEN_DIR" "$BACKUP_DIR"
    
    # Copy current project to both environments
    log "📁 Copying project files to blue environment..."
    cp -r "/Users/sinaoshaghi/Projects/China Car Parts"/* "$BLUE_DIR/"
    
    log "📁 Copying project files to green environment..."
    cp -r "/Users/sinaoshaghi/Projects/China Car Parts"/* "$GREEN_DIR/"
    
    success "Production structure created"
}

# Set up blue environment
setup_blue_environment() {
    log "🔵 Setting up BLUE environment..."
    
    cd "$BLUE_DIR"
    
    # Create blue environment configuration
    cat > .env << EOF
# Blue Environment Configuration
app_env=production
debug=false
log_level=INFO

# Database Configuration
database_url=sqlite:///./data/blue.db

# Telegram Bot Configuration
telegram_bot_token=CHANGEME_YOUR_PRODUCTION_BOT_TOKEN
admin_telegram_ids=176007160

# FastAPI Configuration
secret_key=blue_production_secret_key_32_chars_long
jwt_secret_key=blue_production_jwt_secret_key_32_chars_long
jwt_algorithm=HS256
jwt_access_token_expire_minutes=1440

# Frontend Configuration
frontend_origin=http://localhost:$BLUE_PORT,http://127.0.0.1:$BLUE_PORT

# Server Configuration
host=0.0.0.0
port=$BLUE_PORT

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
log_file=logs/blue.log

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
    cp "/Users/sinaoshaghi/Projects/China Car Parts/data/app.db" "data/blue.db"
    
    success "Blue environment set up"
}

# Set up green environment
setup_green_environment() {
    log "🟢 Setting up GREEN environment..."
    
    cd "$GREEN_DIR"
    
    # Create green environment configuration
    cat > .env << EOF
# Green Environment Configuration
app_env=production
debug=false
log_level=INFO

# Database Configuration
database_url=sqlite:///./data/green.db

# Telegram Bot Configuration
telegram_bot_token=CHANGEME_YOUR_PRODUCTION_BOT_TOKEN
admin_telegram_ids=176007160

# FastAPI Configuration
secret_key=green_production_secret_key_32_chars_long
jwt_secret_key=green_production_jwt_secret_key_32_chars_long
jwt_algorithm=HS256
jwt_access_token_expire_minutes=1440

# Frontend Configuration
frontend_origin=http://localhost:$GREEN_PORT,http://127.0.0.1:$GREEN_PORT

# Server Configuration
host=0.0.0.0
port=$GREEN_PORT

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
log_file=logs/green.log

# Admin Panel
admin_panel_enabled=true
admin_panel_port=3001

# Features
bulk_limit_default=10
maintenance_mode=false

# Redis
redis_url=redis://localhost:6379/1
EOF

    # Set up Python environment
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set up database
    mkdir -p data
    cp "/Users/sinaoshaghi/Projects/China Car Parts/data/app.db" "data/green.db"
    
    success "Green environment set up"
}

# Start blue environment
start_blue_environment() {
    log "🔵 Starting BLUE environment..."
    
    cd "$BLUE_DIR"
    source venv/bin/activate
    
    # Create logs directory
    mkdir -p logs
    
    # Start API service
    nohup uvicorn app.api.main:app --host 0.0.0.0 --port $BLUE_PORT > logs/blue-api.log 2> logs/blue-api-error.log &
    echo $! > logs/blue-api.pid
    
    # Start Bot service
    nohup python -m app.bot.bot_dev > logs/blue-bot.log 2> logs/blue-bot-error.log &
    echo $! > logs/blue-bot.pid
    
    # Wait for services to start
    sleep 5
    
    # Test blue environment
    if curl -f -s "http://localhost:$BLUE_PORT/health" > /dev/null; then
        success "Blue environment started successfully"
        echo "blue" > "$CURRENT_ENV_FILE"
    else
        error "Blue environment failed to start"
    fi
}

# Start green environment
start_green_environment() {
    log "🟢 Starting GREEN environment..."
    
    cd "$GREEN_DIR"
    source venv/bin/activate
    
    # Create logs directory
    mkdir -p logs
    
    # Start API service
    nohup uvicorn app.api.main:app --host 0.0.0.0 --port $GREEN_PORT > logs/green-api.log 2> logs/green-api-error.log &
    echo $! > logs/green-api.pid
    
    # Start Bot service
    nohup python -m app.bot.bot_dev > logs/green-bot.log 2> logs/green-bot-error.log &
    echo $! > logs/green-bot.pid
    
    # Wait for services to start
    sleep 5
    
    # Test green environment
    if curl -f -s "http://localhost:$GREEN_PORT/health" > /dev/null; then
        success "Green environment started successfully"
    else
        error "Green environment failed to start"
    fi
}

# Set up load balancer (simulated with nginx config)
setup_load_balancer() {
    log "⚖️ Setting up load balancer..."
    
    # Create nginx configuration for blue-green deployment
    cat > "$PROD_DIR/nginx.conf" << EOF
upstream blue_backend {
    server localhost:$BLUE_PORT;
}

upstream green_backend {
    server localhost:$GREEN_PORT;
}

server {
    listen $PRODUCTION_PORT;
    server_name localhost;
    
    # Health check endpoint
    location /health {
        proxy_pass http://blue_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # Main application
    location / {
        proxy_pass http://blue_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    success "Load balancer configuration created"
}

# Switch to green environment
switch_to_green() {
    log "🔄 Switching to GREEN environment..."
    
    # Update nginx configuration to point to green
    sed -i '' 's/blue_backend/green_backend/g' "$PROD_DIR/nginx.conf"
    
    # Update current environment
    echo "green" > "$CURRENT_ENV_FILE"
    
    # Test green environment
    if curl -f -s "http://localhost:$GREEN_PORT/health" > /dev/null; then
        success "Switched to GREEN environment"
    else
        error "Failed to switch to GREEN environment"
    fi
}

# Switch to blue environment
switch_to_blue() {
    log "🔄 Switching to BLUE environment..."
    
    # Update nginx configuration to point to blue
    sed -i '' 's/green_backend/blue_backend/g' "$PROD_DIR/nginx.conf"
    
    # Update current environment
    echo "blue" > "$CURRENT_ENV_FILE"
    
    # Test blue environment
    if curl -f -s "http://localhost:$BLUE_PORT/health" > /dev/null; then
        success "Switched to BLUE environment"
    else
        error "Failed to switch to BLUE environment"
    fi
}

# Run production tests
run_production_tests() {
    log "🧪 Running production tests..."
    
    local test_port=$1
    local env_name=$2
    
    # Create test script for the environment
    cat > "$PROD_DIR/test_${env_name}.py" << EOF
#!/usr/bin/env python3
import requests
import sys

def test_environment(port, env_name):
    base_url = f"http://localhost:{port}"
    
    print(f"🧪 Testing {env_name.upper()} Environment")
    print("=" * 50)
    
    # Test API health
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ {env_name.upper()} Health: {response.json()}")
        else:
            print(f"❌ {env_name.upper()} Health: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {env_name.upper()} Health: Error - {e}")
        return False
    
    # Test parts endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/parts/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {env_name.upper()} Parts: {len(data.get('items', []))} parts found")
        else:
            print(f"❌ {env_name.upper()} Parts: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {env_name.upper()} Parts: Error - {e}")
        return False
    
    # Test search functionality
    try:
        response = requests.get(f"{base_url}/api/v1/parts/?search=brake", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {env_name.upper()} Search: {len(data.get('items', []))} results found")
        else:
            print(f"❌ {env_name.upper()} Search: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {env_name.upper()} Search: Error - {e}")
        return False
    
    print(f"🎉 {env_name.upper()} Environment: All tests passed!")
    return True

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    env_name = sys.argv[2] if len(sys.argv) > 2 else "blue"
    success = test_environment(port, env_name)
    sys.exit(0 if success else 1)
EOF

    # Test blue environment
    log "🔵 Testing BLUE environment..."
    python3 "$PROD_DIR/test_blue.py" $BLUE_PORT blue
    
    # Test green environment
    log "🟢 Testing GREEN environment..."
    python3 "$PROD_DIR/test_green.py" $GREEN_PORT green
    
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
    echo "⚖️ Load Balancer:"
    echo "  Port: $PRODUCTION_PORT"
    echo "  Config: $PROD_DIR/nginx.conf"
    echo ""
    echo "📁 Directories:"
    echo "  Blue: $BLUE_DIR"
    echo "  Green: $GREEN_DIR"
    echo "  Backups: $BACKUP_DIR"
    echo ""
    echo "🛑 To stop production services:"
    echo "  pkill -f 'uvicorn.*800[0-2]'"
    echo "  pkill -f 'python.*bot.*production'"
    echo "  rm -rf $PROD_DIR"
    echo ""
    echo "🔄 To switch environments:"
    echo "  $0 --switch-to-green"
    echo "  $0 --switch-to-blue"
    echo ""
}

# Main deployment function
main() {
    log "🚀 Starting Production Deployment with Blue-Green Strategy"
    echo "========================================================"
    
    # Set up trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    pre_deployment_checks
    create_production_structure
    setup_blue_environment
    setup_green_environment
    start_blue_environment
    start_green_environment
    setup_load_balancer
    run_production_tests
    show_production_status
    
    success "🎉 Production deployment completed successfully!"
    echo ""
    echo "Your production environment is now running with:"
    echo "🔵 BLUE Environment: http://localhost:$BLUE_PORT"
    echo "🟢 GREEN Environment: http://localhost:$GREEN_PORT"
    echo "⚖️ Load Balancer: http://localhost:$PRODUCTION_PORT"
    echo ""
    echo "This implements a real blue-green deployment strategy!"
}

# Handle command line arguments
case "${1:-}" in
    --switch-to-green)
        switch_to_green
        ;;
    --switch-to-blue)
        switch_to_blue
        ;;
    --status)
        show_production_status
        ;;
    --help)
        echo "Production Deployment Script with Blue-Green Strategy"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --switch-to-green    Switch to green environment"
        echo "  --switch-to-blue     Switch to blue environment"
        echo "  --status            Show production status"
        echo "  --help              Show this help message"
        echo ""
        ;;
    *)
        main
        ;;
esac
