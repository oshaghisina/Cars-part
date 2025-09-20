#!/bin/bash

# Blue-Green Deployment Script for China Car Parts Production
# This script implements blue-green deployment strategy for zero-downtime deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_DIR="/opt/china-car-parts"
BACKUP_DIR="/opt/backups/china-car-parts"
LOG_FILE="/var/log/china-car-parts-blue-green-deploy.log"
BLUE_PORT=8001
GREEN_PORT=8002
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
ROLLBACK_TIMEOUT=60       # 1 minute

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

# Show help
show_help() {
    echo "Blue-Green Deployment Script for China Car Parts"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --deploy COMMIT_SHA    Deploy specific commit"
    echo "  -s, --switch              Switch blue/green environments"
    echo "  -r, --rollback            Rollback to previous environment"
    echo "  -s, --status              Show current deployment status"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --deploy abc1234"
    echo "  $0 --switch"
    echo "  $0 --rollback"
    echo "  $0 --status"
}

# Get current environment
get_current_environment() {
    if [ -f "$PROD_DIR/.environment" ]; then
        cat "$PROD_DIR/.environment"
    else
        echo "blue"
    fi
}

# Get environment directories
get_environment_dirs() {
    local current_env=$(get_current_environment)
    
    if [ "$current_env" = "blue" ]; then
        CURRENT_DIR="$PROD_DIR-blue"
        NEW_DIR="$PROD_DIR-green"
        CURRENT_PORT=$BLUE_PORT
        NEW_PORT=$GREEN_PORT
    else
        CURRENT_DIR="$PROD_DIR-green"
        NEW_DIR="$PROD_DIR-blue"
        CURRENT_PORT=$GREEN_PORT
        NEW_PORT=$BLUE_PORT
    fi
}

# Health check function
health_check() {
    local port=$1
    local env_name=$2
    local timeout=${3:-$HEALTH_CHECK_TIMEOUT}
    
    log "🩺 Health checking $env_name environment on port $port..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        if curl -f -s "http://localhost:$port/api/v1/health" > /dev/null; then
            success "$env_name environment health check passed"
            return 0
        fi
        
        log "⏳ Health check attempt for $env_name environment..."
        sleep 10
    done
    
    error "$env_name environment health check failed after $timeout seconds"
}

# Validate deployment prerequisites
validate_prerequisites() {
    local target_dir=$1
    local commit_sha=$2
    local port=$3
    local env_name=$4
    
    log "🔍 Validating deployment prerequisites..."
    
    # Check if port is available
    if netstat -tuln | grep -q ":$port "; then
        error "Port $port is already in use. Cannot deploy to $env_name environment."
    fi
    
    # Check if commit SHA is valid
    if [ -z "$commit_sha" ]; then
        error "Commit SHA is required for deployment"
    fi
    
    # Check if we have enough disk space (minimum 1GB)
    local available_space=$(df "$target_dir" 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
    if [ "$available_space" -lt 1048576 ]; then  # 1GB in KB
        warning "Low disk space detected. Available: $(($available_space/1024))MB"
    fi
    
    # Check if required commands exist
    for cmd in git python3.11 pip npm systemctl nginx; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error "Required command '$cmd' not found"
        fi
    done
    
    success "Prerequisites validation passed"
}

# Deploy to environment with enhanced error handling
deploy_to_environment() {
    local target_dir=$1
    local commit_sha=$2
    local port=$3
    local env_name=$4
    
    log "🚀 Deploying to $env_name environment ($target_dir)..."
    
    # Validate prerequisites
    validate_prerequisites "$target_dir" "$commit_sha" "$port" "$env_name"
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_dir" || error "Failed to create target directory: $target_dir"
    
    # Clone or update repository with error handling
    if [ -d "$target_dir/.git" ]; then
        log "📥 Updating existing repository..."
        cd "$target_dir" || error "Failed to change to target directory: $target_dir"
        
        # Backup current state
        git stash push -m "Deployment backup $(date)" || warning "No changes to stash"
        
        if ! git fetch origin; then
            error "Failed to fetch from origin repository"
        fi
        
        if ! git reset --hard "$commit_sha"; then
            error "Failed to reset to commit: $commit_sha"
        fi
    else
        log "📥 Cloning repository..."
        if ! git clone https://github.com/your-org/china-car-parts.git "$target_dir"; then
            error "Failed to clone repository to: $target_dir"
        fi
        
        cd "$target_dir" || error "Failed to change to target directory: $target_dir"
        
        if ! git checkout "$commit_sha"; then
            error "Failed to checkout commit: $commit_sha"
        fi
    fi
    
    # Set up Python environment with error handling
    log "🐍 Setting up Python environment..."
    if [ ! -d "$target_dir/venv" ]; then
        if ! python3.11 -m venv "$target_dir/venv"; then
            error "Failed to create Python virtual environment"
        fi
    fi
    
    if ! source "$target_dir/venv/bin/activate"; then
        error "Failed to activate Python virtual environment"
    fi
    
    # Upgrade pip first
    pip install --upgrade pip || warning "Failed to upgrade pip"
    
    # Install dependencies with retry logic
    local pip_attempts=0
    local max_pip_attempts=3
    while [ $pip_attempts -lt $max_pip_attempts ]; do
        if pip install -r requirements.txt; then
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
    
    # Run database migrations with backup
    log "🗄️ Running database migrations..."
    local db_backup_file="$BACKUP_DIR/${env_name}_db_backup_$(date +%Y%m%d_%H%M%S).db"
    if [ -f "$target_dir/data/china_car_parts.db" ]; then
        mkdir -p "$BACKUP_DIR"
        cp "$target_dir/data/china_car_parts.db" "$db_backup_file" || warning "Failed to backup database"
        log "📦 Database backed up to: $db_backup_file"
    fi
    
    if ! alembic upgrade head; then
        error "Database migration failed. Check database connection and migration files."
    fi
    
    # Build frontend with error handling
    log "🎨 Building frontend..."
    if [ ! -d "$target_dir/app/frontend/panel" ]; then
        error "Frontend directory not found: $target_dir/app/frontend/panel"
    fi
    
    cd "$target_dir/app/frontend/panel" || error "Failed to change to frontend directory"
    
    # Install npm dependencies with retry logic
    local npm_attempts=0
    local max_npm_attempts=3
    while [ $npm_attempts -lt $max_npm_attempts ]; do
        if npm ci; then
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
    
    if ! npm run build; then
        error "Frontend build failed. Check for build errors."
    fi
    
    cd "$target_dir" || error "Failed to return to project root"
    
    # Copy environment configuration
    if [ -f "$target_dir/deployment/configs/production.env" ]; then
        cp "$target_dir/deployment/configs/production.env" "$target_dir/.env" || error "Failed to copy environment configuration"
    else
        warning "Production environment configuration not found, using defaults"
    fi
    
    # Update systemd services with validation
    log "⚙️ Configuring systemd services..."
    if [ ! -f "$target_dir/deployment/configs/china-car-parts-api.service" ]; then
        error "API service configuration not found"
    fi
    
    if [ ! -f "$target_dir/deployment/configs/china-car-parts-bot.service" ]; then
        error "Bot service configuration not found"
    fi
    
    sed "s|/opt/china-car-parts|$target_dir|g" "$target_dir/deployment/configs/china-car-parts-api.service" > "/etc/systemd/system/china-car-parts-api-$env_name.service" || error "Failed to create API service file"
    sed "s|/opt/china-car-parts|$target_dir|g" "$target_dir/deployment/configs/china-car-parts-bot.service" > "/etc/systemd/system/china-car-parts-bot-$env_name.service" || error "Failed to create bot service file"
    
    # Update port in service files
    sed -i "s|--port 8001|--port $port|g" "/etc/systemd/system/china-car-parts-api-$env_name.service" || error "Failed to update API service port"
    
    # Reload systemd
    if ! systemctl daemon-reload; then
        error "Failed to reload systemd daemon"
    fi
    
    # Enable and start services with error handling
    log "🚀 Starting services..."
    systemctl enable "china-car-parts-api-$env_name" || error "Failed to enable API service"
    systemctl enable "china-car-parts-bot-$env_name" || error "Failed to enable bot service"
    
    if ! systemctl start "china-car-parts-api-$env_name"; then
        error "Failed to start API service. Check logs with: journalctl -u china-car-parts-api-$env_name"
    fi
    
    if ! systemctl start "china-car-parts-bot-$env_name"; then
        error "Failed to start bot service. Check logs with: journalctl -u china-car-parts-bot-$env_name"
    fi
    
    # Wait for services to start with validation
    log "⏳ Waiting for services to start..."
    sleep 15
    
    # Verify services are running
    if ! systemctl is-active --quiet "china-car-parts-api-$env_name"; then
        error "API service is not running after start"
    fi
    
    if ! systemctl is-active --quiet "china-car-parts-bot-$env_name"; then
        error "Bot service is not running after start"
    fi
    
    # Health check
    health_check "$port" "$env_name"
    
    success "$env_name environment deployed successfully"
}

# Switch environments
switch_environments() {
    local current_env=$(get_current_environment)
    get_environment_dirs
    
    log "🔄 Switching from $current_env to $([ "$current_env" = "blue" ] && echo "green" || echo "blue") environment..."
    
    # Update load balancer configuration
    local new_env=$([ "$current_env" = "blue" ] && echo "green" || echo "blue")
    local new_port=$([ "$new_env" = "blue" ] && echo $BLUE_PORT || echo $GREEN_PORT)
    
    # Update Nginx configuration
    sed "s|server 127.0.0.1:8001.*|server 127.0.0.1:$new_port weight=1 max_fails=3 fail_timeout=30s;|g" /etc/nginx/sites-available/china-car-parts > /tmp/nginx-config
    mv /tmp/nginx-config /etc/nginx/sites-available/china-car-parts
    
    # Test Nginx configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    # Wait for load balancer to switch
    sleep 10
    
    # Final health check through load balancer
    log "🩺 Final health check through load balancer..."
    for i in {1..5}; do
        if curl -f -s "https://5.223.59.155/api/v1/health" > /dev/null; then
            success "Load balancer health check passed"
            break
        else
            warning "Load balancer health check attempt $i/5 failed, retrying in 5s..."
            sleep 5
        fi
    done
    
    # Stop old environment services
    log "⏹️ Stopping $current_env environment services..."
    systemctl stop "china-car-parts-api-$current_env" || true
    systemctl stop "china-car-parts-bot-$current_env" || true
    
    # Update environment marker
    echo "$new_env" > "$NEW_DIR/.environment"
    
    # Create backup of old environment
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)-$current_env"
    mkdir -p "$BACKUP_DIR"
    cp -r "$CURRENT_DIR" "$BACKUP_DIR/$backup_name"
    
    success "Environment switch completed successfully"
    log "📍 Active environment: $new_env"
    log "📍 API Port: $new_port"
    log "📦 Backup created: $backup_name"
}

# Rollback function
rollback() {
    local current_env=$(get_current_environment)
    get_environment_dirs
    
    log "🔄 Rolling back from $current_env environment..."
    
    # Determine rollback environment
    local rollback_env=$([ "$current_env" = "blue" ] && echo "green" || echo "blue")
    local rollback_dir=$([ "$rollback_env" = "blue" ] && echo "$PROD_DIR-blue" || echo "$PROD_DIR-green")
    local rollback_port=$([ "$rollback_env" = "blue" ] && echo $BLUE_PORT || echo $GREEN_PORT)
    
    # Check if rollback environment exists
    if [ ! -d "$rollback_dir" ]; then
        error "Rollback environment $rollback_env does not exist"
    fi
    
    # Start rollback environment services
    log "🚀 Starting rollback environment services..."
    systemctl start "china-car-parts-api-$rollback_env"
    systemctl start "china-car-parts-bot-$rollback_env"
    
    # Health check rollback environment
    health_check "$rollback_port" "$rollback_env" $ROLLBACK_TIMEOUT
    
    # Switch to rollback environment
    log "🔄 Switching to rollback environment..."
    
    # Update Nginx configuration
    sed "s|server 127.0.0.1:8001.*|server 127.0.0.1:$rollback_port weight=1 max_fails=3 fail_timeout=30s;|g" /etc/nginx/sites-available/china-car-parts > /tmp/nginx-config
    mv /tmp/nginx-config /etc/nginx/sites-available/china-car-parts
    
    # Test and reload Nginx
    nginx -t
    systemctl reload nginx
    
    # Stop current environment services
    systemctl stop "china-car-parts-api-$current_env"
    systemctl stop "china-car-parts-bot-$current_env"
    
    # Update environment marker
    echo "$rollback_env" > "$rollback_dir/.environment"
    
    success "Rollback completed successfully"
    log "📍 Active environment: $rollback_env"
    log "📍 API Port: $rollback_port"
}

# Show deployment status
show_status() {
    local current_env=$(get_current_environment)
    get_environment_dirs
    
    echo "📊 Blue-Green Deployment Status"
    echo "================================"
    echo ""
    echo "📍 Current Environment: $current_env"
    echo "📍 Current Port: $CURRENT_PORT"
    echo "📍 Current Directory: $CURRENT_DIR"
    echo ""
    
    # Check service status
    echo "🔧 Service Status:"
    echo "  API ($current_env): $(systemctl is-active china-car-parts-api-$current_env 2>/dev/null || echo 'inactive')"
    echo "  Bot ($current_env): $(systemctl is-active china-car-parts-bot-$current_env 2>/dev/null || echo 'inactive')"
    echo ""
    
    # Check other environment
    local other_env=$([ "$current_env" = "blue" ] && echo "green" || echo "blue")
    echo "🔧 Other Environment ($other_env):"
    echo "  API ($other_env): $(systemctl is-active china-car-parts-api-$other_env 2>/dev/null || echo 'inactive')"
    echo "  Bot ($other_env): $(systemctl is-active china-car-parts-bot-$other_env 2>/dev/null || echo 'inactive')"
    echo ""
    
    # Check load balancer
    echo "⚖️ Load Balancer:"
    echo "  Nginx: $(systemctl is-active nginx 2>/dev/null || echo 'inactive')"
    echo ""
    
    # Check health
    echo "🩺 Health Status:"
    if curl -f -s "https://5.223.59.155/api/v1/health" > /dev/null; then
        echo "  Production: ✅ Healthy"
    else
        echo "  Production: ❌ Unhealthy"
    fi
}

# Main deployment function
deploy() {
    local commit_sha=$1
    
    if [ -z "$commit_sha" ]; then
        error "Commit SHA is required for deployment"
    fi
    
    log "🚀 Starting blue-green deployment for commit: $commit_sha"
    
    # Get current environment
    local current_env=$(get_current_environment)
    get_environment_dirs
    
    log "📍 Current environment: $current_env"
    log "📍 Deploying to: $([ "$current_env" = "blue" ] && echo "green" || echo "blue")"
    
    # Deploy to new environment
    deploy_to_environment "$NEW_DIR" "$commit_sha" "$NEW_PORT" "$([ "$current_env" = "blue" ] && echo "green" || echo "blue")"
    
    # Switch environments
    switch_environments
    
    success "Blue-green deployment completed successfully!"
}

# Main execution
main() {
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    case "${1:-}" in
        -d|--deploy)
            deploy "$2"
            ;;
        -s|--switch)
            switch_environments
            ;;
        -r|--rollback)
            rollback
            ;;
        --status)
            show_status
            ;;
        -h|--help)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            error "Unknown option: $1. Use --help for usage information."
            ;;
    esac
}

# Run main function
main "$@"
