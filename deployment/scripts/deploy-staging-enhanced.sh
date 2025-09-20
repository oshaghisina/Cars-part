#!/bin/bash

# Enhanced staging deployment script with comprehensive error handling and monitoring
# This script deploys the application to the staging server with full validation

set -e # Exit immediately if a command exits with a non-zero status

# Configuration
REPO_DIR="/opt/china-car-parts-staging"
VENV_DIR="$REPO_DIR/venv"
API_SERVICE="china-car-parts-api-staging"
BOT_SERVICE="china-car-parts-bot-staging"
FRONTEND_DIR="$REPO_DIR/app/frontend/panel"
LOG_FILE="/var/log/china-car-parts-staging-deploy.log"
BACKUP_DIR="/opt/backups/china-car-parts-staging"
MAX_BACKUPS=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if repository directory exists
    if [ ! -d "$REPO_DIR" ]; then
        error "Repository directory $REPO_DIR does not exist"
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        error "Virtual environment $VENV_DIR does not exist"
    fi
    
    # Check if systemd services exist
    if ! systemctl list-unit-files | grep -q "$API_SERVICE"; then
        error "API service $API_SERVICE is not configured"
    fi
    
    if ! systemctl list-unit-files | grep -q "$BOT_SERVICE"; then
        error "Bot service $BOT_SERVICE is not configured"
    fi
    
    # Check disk space (require at least 1GB free)
    AVAILABLE_SPACE=$(df "$REPO_DIR" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then
        error "Insufficient disk space. Available: ${AVAILABLE_SPACE}KB, Required: 1GB"
    fi
    
    # Check if .env file exists
    if [ ! -f "$REPO_DIR/.env" ]; then
        warning ".env file not found at $REPO_DIR/.env"
    fi
    
    success "Pre-deployment checks passed"
}

# Create backup
create_backup() {
    log "📦 Creating backup of current deployment..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Create timestamped backup
    BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    # Backup current deployment
    cp -r "$REPO_DIR" "$BACKUP_PATH"
    
    # Clean old backups (keep only last MAX_BACKUPS)
    cd "$BACKUP_DIR"
    ls -t | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -rf
    
    success "Backup created: $BACKUP_NAME"
    echo "$BACKUP_NAME" > "$BACKUP_DIR/latest"
}

# Deploy application
deploy_application() {
    log "🚀 Starting deployment to staging environment..."
    
    # Navigate to the repository directory
    cd $REPO_DIR
    
    # Pull the latest changes from the staging branch
    log "📥 Pulling latest changes from staging branch..."
    git fetch origin
    git reset --hard origin/staging
    
    # Activate virtual environment
    log "🐍 Activating virtual environment..."
    source $VENV_DIR/bin/activate
    
    # Install/update backend dependencies
    log "📦 Installing/updating backend dependencies..."
    pip install -r requirements.txt
    
    # Run database migrations
    log "🗄️ Running database migrations..."
    alembic upgrade head
    
    # Build frontend
    log "🎨 Building frontend for staging..."
    cd $FRONTEND_DIR
    npm ci # Install frontend dependencies
    npm run build # Build the frontend
    cd $REPO_DIR # Go back to repo root
    
    success "Application deployment completed"
}

# Restart services
restart_services() {
    log "🔄 Restarting services..."
    
    # Stop services gracefully
    log "Stopping API service ($API_SERVICE)..."
    sudo systemctl stop $API_SERVICE
    
    log "Stopping Bot service ($BOT_SERVICE)..."
    sudo systemctl stop $BOT_SERVICE
    
    # Wait a moment for graceful shutdown
    sleep 5
    
    # Start services
    log "Starting API service ($API_SERVICE)..."
    sudo systemctl start $API_SERVICE
    
    log "Starting Bot service ($BOT_SERVICE)..."
    sudo systemctl start $BOT_SERVICE
    
    # Wait for services to start
    log "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service status
    if systemctl is-active --quiet $API_SERVICE; then
        success "API service is running"
    else
        error "API service failed to start"
    fi
    
    if systemctl is-active --quiet $BOT_SERVICE; then
        success "Bot service is running"
    else
        error "Bot service failed to start"
    fi
}

# Health checks
health_checks() {
    log "🩺 Running health checks..."
    
    # Wait for services to be ready
    sleep 15
    
    # Check API health
    API_URL="http://localhost:8001"
    for i in {1..10}; do
        if curl -f -s "$API_URL/health" > /dev/null; then
            success "API health check passed"
            break
        else
            warning "API health check attempt $i/10 failed, retrying in 10s..."
            sleep 10
        fi
        
        if [ $i -eq 10 ]; then
            error "API health check failed after 10 attempts"
        fi
    done
    
    # Check service logs for errors
    log "📋 Checking service logs for errors..."
    
    # Check API service logs for errors in the last 5 minutes
    API_ERRORS=$(journalctl -u $API_SERVICE --since "5 minutes ago" | grep -i error | wc -l)
    if [ "$API_ERRORS" -gt 0 ]; then
        warning "Found $API_ERRORS errors in API service logs"
        journalctl -u $API_SERVICE --since "5 minutes ago" | grep -i error | tail -5
    fi
    
    # Check Bot service logs for errors in the last 5 minutes
    BOT_ERRORS=$(journalctl -u $BOT_SERVICE --since "5 minutes ago" | grep -i error | wc -l)
    if [ "$BOT_ERRORS" -gt 0 ]; then
        warning "Found $BOT_ERRORS errors in Bot service logs"
        journalctl -u $BOT_SERVICE --since "5 minutes ago" | grep -i error | tail -5
    fi
    
    success "Health checks completed"
}

# Rollback function
rollback() {
    log "🔄 Rolling back to previous deployment..."
    
    if [ ! -f "$BACKUP_DIR/latest" ]; then
        error "No backup found for rollback"
    fi
    
    LATEST_BACKUP=$(cat "$BACKUP_DIR/latest")
    BACKUP_PATH="$BACKUP_DIR/$LATEST_BACKUP"
    
    if [ ! -d "$BACKUP_PATH" ]; then
        error "Backup directory $BACKUP_PATH not found"
    fi
    
    # Stop services
    sudo systemctl stop $API_SERVICE
    sudo systemctl stop $BOT_SERVICE
    
    # Restore from backup
    rm -rf "$REPO_DIR"
    cp -r "$BACKUP_PATH" "$REPO_DIR"
    
    # Restart services
    sudo systemctl start $API_SERVICE
    sudo systemctl start $BOT_SERVICE
    
    success "Rollback completed to backup: $LATEST_BACKUP"
}

# Main execution
main() {
    log "🚀 Starting enhanced staging deployment..."
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    pre_deployment_checks
    create_backup
    
    # Set up error handling for rollback
    trap 'error "Deployment failed. Consider running rollback manually."' ERR
    
    deploy_application
    restart_services
    health_checks
    
    success "✅ Deployment to staging completed successfully!"
    
    # Display deployment summary
    log "📊 Deployment Summary:"
    log "  - Repository: $REPO_DIR"
    log "  - API Service: $API_SERVICE ($(systemctl is-active $API_SERVICE))"
    log "  - Bot Service: $BOT_SERVICE ($(systemctl is-active $BOT_SERVICE))"
    log "  - Backup: $(cat $BACKUP_DIR/latest)"
    log "  - Log: $LOG_FILE"
}

# Handle command line arguments
case "${1:-}" in
    "rollback")
        rollback
        ;;
    "health-check")
        health_checks
        ;;
    "backup")
        create_backup
        ;;
    *)
        main
        ;;
esac
