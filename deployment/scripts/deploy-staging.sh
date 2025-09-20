#!/bin/bash

# 🚀 Staging Deployment Script
# This script deploys the application to the staging environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_DIR="/opt/china-car-parts"
STAGING_USER="${STAGING_USER:-staging}"
STAGING_HOST="${STAGING_HOST:-staging.yourdomain.com}"
BRANCH="${BRANCH:-staging}"
LOG_FILE="/var/log/china-car-parts-staging-deploy.log"

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

# Validate deployment prerequisites
validate_prerequisites() {
    log "🔍 Validating staging deployment prerequisites..."
    
    # Check if SSH connection works
    if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$STAGING_USER@$STAGING_HOST" "echo 'SSH connection successful'" >/dev/null 2>&1; then
        error "Cannot connect to staging server: $STAGING_USER@$STAGING_HOST"
    fi
    
    # Check if staging directory exists
    if ! run_staging "test -d $STAGING_DIR"; then
        error "Staging directory does not exist: $STAGING_DIR"
    fi
    
    # Check if required commands exist on remote server
    for cmd in git python3.11 pip npm systemctl; do
        if ! run_staging "command -v $cmd >/dev/null 2>&1"; then
            error "Required command '$cmd' not found on staging server"
        fi
    done
    
    # Check if branch exists
    if ! run_staging "cd $STAGING_DIR && git ls-remote --heads origin $BRANCH | grep -q $BRANCH"; then
        error "Branch '$BRANCH' does not exist in remote repository"
    fi
    
    success "Prerequisites validation passed"
}

log "🚀 Starting staging deployment..."
log "📁 Target: $STAGING_USER@$STAGING_HOST:$STAGING_DIR"
log "🌿 Branch: $BRANCH"

# Function to execute commands on staging server
run_staging() {
    ssh -o StrictHostKeyChecking=no "$STAGING_USER@$STAGING_HOST" "$@"
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service_name service..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_staging "systemctl is-active --quiet $service_name"; then
            echo "✅ $service_name is running"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to run health check
health_check() {
    local max_attempts=10
    local attempt=1
    local api_url="${STAGING_API_URL:-http://localhost:8001}"
    
    echo "🏥 Running health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_staging "curl -f -s $api_url/api/v1/health > /dev/null"; then
            echo "✅ Health check passed"
            return 0
        fi
        
        echo "⏳ Health check attempt $attempt/$max_attempts..."
        sleep 5
        ((attempt++))
    done
    
    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Main deployment process with enhanced error handling
main() {
    log "📋 Starting pre-deployment validation..."
    validate_prerequisites
    
    # Create database backup before deployment
    log "📦 Creating database backup..."
    local backup_file="$STAGING_DIR/backups/staging_db_backup_$(date +%Y%m%d_%H%M%S).db"
    run_staging "mkdir -p $STAGING_DIR/backups"
    run_staging "cp $STAGING_DIR/data/china_car_parts.db $backup_file 2>/dev/null || warning 'No database file to backup'"
    log "📦 Database backed up to: $backup_file"
    
    log "📥 Pulling latest code from $BRANCH branch..."
    if ! run_staging "cd $STAGING_DIR && git fetch origin"; then
        error "Failed to fetch from origin repository"
    fi
    
    if ! run_staging "cd $STAGING_DIR && git checkout $BRANCH"; then
        error "Failed to checkout branch: $BRANCH"
    fi
    
    if ! run_staging "cd $STAGING_DIR && git pull origin $BRANCH"; then
        error "Failed to pull latest changes from $BRANCH"
    fi
    
    # Get current commit hash for logging
    local current_commit=$(run_staging "cd $STAGING_DIR && git rev-parse --short HEAD")
    log "📝 Deploying commit: $current_commit"
    
    log "🐍 Setting up Python environment..."
    if ! run_staging "cd $STAGING_DIR && test -d venv"; then
        error "Python virtual environment not found at $STAGING_DIR/venv"
    fi
    
    if ! run_staging "cd $STAGING_DIR && source venv/bin/activate && pip install --upgrade pip"; then
        warning "Failed to upgrade pip, continuing with existing version"
    fi
    
    # Install dependencies with retry logic
    local pip_attempts=0
    local max_pip_attempts=3
    while [ $pip_attempts -lt $max_pip_attempts ]; do
        if run_staging "cd $STAGING_DIR && source venv/bin/activate && pip install -r requirements.txt"; then
            break
        else
            pip_attempts=$((pip_attempts + 1))
            if [ $pip_attempts -eq $max_pip_attempts ]; then
                error "Failed to install Python dependencies after $max_pip_attempts attempts"
            fi
            warning "Pip install failed, retrying... (attempt $pip_attempts/$max_pip_attempts)"
            sleep 5
        fi
    done
    
    log "🗄️ Running database migrations..."
    if ! run_staging "cd $STAGING_DIR && source venv/bin/activate && alembic upgrade head"; then
        error "Database migration failed. Check database connection and migration files."
    fi
    
    log "📦 Building frontend..."
    if ! run_staging "test -d $STAGING_DIR/app/frontend/panel"; then
        error "Frontend directory not found: $STAGING_DIR/app/frontend/panel"
    fi
    
    # Install npm dependencies with retry logic
    local npm_attempts=0
    local max_npm_attempts=3
    while [ $npm_attempts -lt $max_npm_attempts ]; do
        if run_staging "cd $STAGING_DIR/app/frontend/panel && npm ci"; then
            break
        else
            npm_attempts=$((npm_attempts + 1))
            if [ $npm_attempts -eq $max_npm_attempts ]; then
                error "Failed to install npm dependencies after $max_npm_attempts attempts"
            fi
            warning "Npm ci failed, retrying... (attempt $npm_attempts/$max_npm_attempts)"
            sleep 5
        fi
    done
    
    if ! run_staging "cd $STAGING_DIR/app/frontend/panel && npm run build"; then
        error "Frontend build failed. Check for build errors."
    fi
    
    log "🔄 Restarting services..."
    
    # Stop services gracefully
    log "⏹️ Stopping existing services..."
    run_staging "sudo systemctl stop china-car-parts-api-staging 2>/dev/null || warning 'API service was not running'"
    run_staging "sudo systemctl stop china-car-parts-bot-staging 2>/dev/null || warning 'Bot service was not running'"
    
    # Start API service
    log "🚀 Starting API service..."
    if ! run_staging "sudo systemctl start china-car-parts-api-staging"; then
        error "Failed to start API service. Check logs with: ssh $STAGING_USER@$STAGING_HOST 'journalctl -u china-car-parts-api-staging'"
    fi
    check_service "china-car-parts-api-staging"
    
    # Start Bot service
    log "🤖 Starting Bot service..."
    if ! run_staging "sudo systemctl start china-car-parts-bot-staging"; then
        error "Failed to start Bot service. Check logs with: ssh $STAGING_USER@$STAGING_HOST 'journalctl -u china-car-parts-bot-staging'"
    fi
    check_service "china-car-parts-bot-staging"
    
    # Reload Nginx
    log "🌐 Reloading Nginx..."
    if ! run_staging "sudo systemctl reload nginx"; then
        error "Failed to reload Nginx. Check configuration with: ssh $STAGING_USER@$STAGING_HOST 'nginx -t'"
    fi
    
    # Health check
    health_check
    
    success "Staging deployment completed successfully!"
    log "🌐 Staging URL: https://staging.yourdomain.com"
    log "📊 API Health: https://staging.yourdomain.com/api/v1/health"
    log "📝 Deployed commit: $current_commit"
}

# Enhanced error handling
trap 'error "Deployment failed at line $LINENO. Check logs for details."' ERR

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Staging Deployment Script for China Car Parts"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  STAGING_USER     SSH user for staging server (default: staging)"
    echo "  STAGING_HOST     Staging server hostname (default: staging.yourdomain.com)"
    echo "  BRANCH           Git branch to deploy (default: staging)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy staging branch"
    echo "  BRANCH=feature-branch $0              # Deploy specific branch"
    echo "  STAGING_HOST=staging.example.com $0   # Deploy to specific server"
    exit 0
fi

# Run main function
main "$@"
