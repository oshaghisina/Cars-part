#!/bin/bash

# 🚀 Deploy to Production Server Script
# This script deploys the application to a production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROD_USER="${PROD_USER:-partsbot}"
PROD_HOST="${PROD_HOST:-yourdomain.com}"
PROD_DIR="/opt/china-car-parts"
BRANCH="${BRANCH:-main}"
BACKUP_DIR="/opt/backups/china-car-parts"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Function to execute commands on production server
run_production() {
    ssh -o StrictHostKeyChecking=no "$PROD_USER@$PROD_HOST" "$@"
}

# Function to create database backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/china_car_parts_$timestamp.sql"
    
    log "💾 Creating database backup..."
    
    run_production "mkdir -p $BACKUP_DIR"
    run_production "pg_dump china_car_parts_production > $backup_file"
    run_production "gzip $backup_file"
    
    success "Database backup created: ${backup_file}.gz"
    
    # Keep only last 10 backups
    run_production "ls -t $BACKUP_DIR/*.gz | tail -n +11 | xargs -r rm"
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    log "🔍 Checking $service_name service..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_production "systemctl is-active --quiet $service_name"; then
            success "$service_name is running"
            return 0
        fi
        
        log "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
    
    error "$service_name failed to start after $max_attempts attempts"
}

# Function to run health check
health_check() {
    local max_attempts=15
    local attempt=1
    local api_url="https://$PROD_HOST"
    
    log "🏥 Running production health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_production "curl -f -s $api_url/api/v1/health > /dev/null"; then
            success "Production health check passed"
            return 0
        fi
        
        log "⏳ Health check attempt $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    
    error "Production health check failed after $max_attempts attempts"
}

# Function to rollback deployment
rollback() {
    log "🔄 Starting rollback procedure..."
    
    # Stop current services
    run_production "sudo systemctl stop china-car-parts-api || true"
    run_production "sudo systemctl stop china-car-parts-bot || true"
    
    # Restore from backup (if needed)
    log "📦 Rollback completed - manual intervention may be required"
    log "🔗 Check logs: journalctl -u china-car-parts-api -f"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if production directory exists
    if ! run_production "test -d $PROD_DIR"; then
        error "Production directory $PROD_DIR does not exist. Please run setup_production_server.sh first."
    fi
    
    # Check if we can connect to the server
    if ! run_production "echo 'Connection test successful'"; then
        error "Cannot connect to production server. Check SSH configuration."
    fi
    
    success "Pre-deployment checks passed"
}

# Deploy application
deploy_application() {
    log "📥 Deploying application..."
    
    # Create backup before deployment
    create_backup
    
    # Pull latest code
    log "📥 Pulling latest code..."
    run_production "cd $PROD_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH"
    
    # Update Python dependencies
    log "🐍 Updating Python dependencies..."
    run_production "cd $PROD_DIR && source venv/bin/activate && pip install -r requirements.txt"
    
    # Run database migrations
    log "🗄️ Running database migrations..."
    run_production "cd $PROD_DIR && source venv/bin/activate && alembic upgrade head"
    
    # Build frontend
    log "📦 Building frontend..."
    run_production "cd $PROD_DIR/app/frontend/panel && npm ci && npm run build"
    
    success "Application deployed"
}

# Restart services
restart_services() {
    log "🔄 Restarting services..."
    
    # Stop services gracefully
    log "⏹️ Stopping services..."
    run_production "sudo systemctl stop china-car-parts-api || true"
    run_production "sudo systemctl stop china-car-parts-bot || true"
    
    # Wait for services to stop
    sleep 5
    
    # Start API service
    log "🚀 Starting API service..."
    run_production "sudo systemctl start china-car-parts-api"
    check_service "china-car-parts-api"
    
    # Start Bot service
    log "🤖 Starting Bot service..."
    run_production "sudo systemctl start china-car-parts-bot"
    check_service "china-car-parts-bot"
    
    # Reload Nginx
    log "🌐 Reloading Nginx..."
    run_production "sudo systemctl reload nginx"
    
    # Wait for services to stabilize
    log "⏳ Waiting for services to stabilize..."
    sleep 30
    
    success "Services restarted"
}

# Main deployment process
main() {
    log "🚀 Starting production deployment..."
    log "📁 Target: $PROD_USER@$PROD_HOST:$PROD_DIR"
    log "🌿 Branch: $BRANCH"
    log "⚠️  PRODUCTION DEPLOYMENT - Proceed with caution!"
    
    pre_deployment_checks
    deploy_application
    restart_services
    health_check
    
    success "✅ Production deployment completed successfully!"
    log "🌐 Production URL: https://$PROD_HOST"
    log "📊 API Health: https://$PROD_HOST/api/v1/health"
    log "📈 Monitor logs: journalctl -u china-car-parts-api -f"
}

# Error handling with rollback
trap 'log "❌ Production deployment failed at line $LINENO"; rollback; exit 1' ERR

# Confirmation prompt (for manual runs)
if [ "${SKIP_CONFIRMATION:-false}" != "true" ]; then
    log "⚠️  WARNING: This will deploy to PRODUCTION!"
    log "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
    sleep 10
fi

# Check parameters
if [ -z "$PROD_HOST" ] || [ "$PROD_HOST" = "yourdomain.com" ]; then
    error "Please set PROD_HOST environment variable or pass it as parameter"
fi

# Run main function
main "$@"
