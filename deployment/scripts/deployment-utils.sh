#!/bin/bash

# 🛠️ Deployment Utilities
# Shared functions for deployment scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_to_file() {
    local log_file="$1"
    local message="$2"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $message" | tee -a "$log_file"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

error_to_file() {
    local log_file="$1"
    local message="$2"
    echo -e "${RED}[ERROR]${NC} $message" | tee -a "$log_file" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

warning_to_file() {
    local log_file="$1"
    local message="$2"
    echo -e "${YELLOW}[WARNING]${NC} $message" | tee -a "$log_file"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

success_to_file() {
    local log_file="$1"
    local message="$2"
    echo -e "${GREEN}[SUCCESS]${NC} $message" | tee -a "$log_file"
}

# Health check function
health_check_endpoint() {
    local url="$1"
    local timeout="${2:-300}"
    local max_attempts="${3:-30}"
    local attempt=1
    
    log "🩺 Health checking endpoint: $url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "Health check passed for $url"
            return 0
        fi
        
        log "⏳ Health check attempt $attempt/$max_attempts for $url..."
        sleep $((timeout / max_attempts))
        ((attempt++))
    done
    
    error "Health check failed for $url after $max_attempts attempts"
}

# Service management functions
check_service_status() {
    local service_name="$1"
    local max_attempts="${2:-30}"
    local attempt=1
    
    log "🔍 Checking service status: $service_name"
    
    while [ $attempt -le $max_attempts ]; do
        if systemctl is-active --quiet "$service_name"; then
            success "Service $service_name is running"
            return 0
        fi
        
        log "⏳ Waiting for service $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    error "Service $service_name failed to start after $max_attempts attempts"
}

start_service_safely() {
    local service_name="$1"
    local log_file="${2:-/dev/null}"
    
    log "🚀 Starting service: $service_name"
    
    if ! systemctl start "$service_name"; then
        error_to_file "$log_file" "Failed to start service $service_name. Check logs with: journalctl -u $service_name"
    fi
    
    check_service_status "$service_name"
    success_to_file "$log_file" "Service $service_name started successfully"
}

stop_service_safely() {
    local service_name="$1"
    local log_file="${2:-/dev/null}"
    
    log "⏹️ Stopping service: $service_name"
    
    if systemctl is-active --quiet "$service_name"; then
        if ! systemctl stop "$service_name"; then
            warning_to_file "$log_file" "Failed to stop service $service_name gracefully"
        else
            success_to_file "$log_file" "Service $service_name stopped successfully"
        fi
    else
        log "Service $service_name was not running"
    fi
}

# Database backup function
create_database_backup() {
    local db_path="$1"
    local backup_dir="$2"
    local env_name="$3"
    local log_file="${4:-/dev/null}"
    
    log "📦 Creating database backup..."
    
    if [ ! -f "$db_path" ]; then
        warning_to_file "$log_file" "Database file not found: $db_path"
        return 0
    fi
    
    local backup_file="$backup_dir/${env_name}_db_backup_$(date +%Y%m%d_%H%M%S).db"
    mkdir -p "$backup_dir"
    
    if cp "$db_path" "$backup_file"; then
        success_to_file "$log_file" "Database backed up to: $backup_file"
        echo "$backup_file"  # Return backup file path
    else
        error_to_file "$log_file" "Failed to create database backup"
    fi
}

# Git operations with error handling
git_update_repository() {
    local repo_dir="$1"
    local branch="$2"
    local log_file="${3:-/dev/null}"
    
    log "📥 Updating repository in $repo_dir..."
    
    cd "$repo_dir" || error_to_file "$log_file" "Failed to change to repository directory: $repo_dir"
    
    # Fetch latest changes
    if ! git fetch origin; then
        error_to_file "$log_file" "Failed to fetch from origin repository"
    fi
    
    # Checkout branch
    if ! git checkout "$branch"; then
        error_to_file "$log_file" "Failed to checkout branch: $branch"
    fi
    
    # Pull latest changes
    if ! git pull origin "$branch"; then
        error_to_file "$log_file" "Failed to pull latest changes from $branch"
    fi
    
    # Get current commit hash
    local current_commit=$(git rev-parse --short HEAD)
    success_to_file "$log_file" "Repository updated to commit: $current_commit"
    echo "$current_commit"  # Return commit hash
}

# Dependency installation with retry logic
install_dependencies_with_retry() {
    local install_command="$1"
    local max_attempts="${2:-3}"
    local log_file="${3:-/dev/null}"
    local attempt=1
    
    log "📦 Installing dependencies with retry logic..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval "$install_command"; then
            success_to_file "$log_file" "Dependencies installed successfully"
            return 0
        else
            if [ $attempt -eq $max_attempts ]; then
                error_to_file "$log_file" "Failed to install dependencies after $max_attempts attempts"
            fi
            warning_to_file "$log_file" "Installation failed, retrying... (attempt $attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        fi
    done
}

# System resource checks
check_system_resources() {
    local log_file="${1:-/dev/null}"
    
    log "🔍 Checking system resources..."
    
    # Check disk space (minimum 1GB free)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 1048576 ]; then  # 1GB in KB
        warning_to_file "$log_file" "Low disk space detected. Available: $(($available_space/1024))MB"
    else
        success_to_file "$log_file" "Sufficient disk space available: $(($available_space/1024))MB"
    fi
    
    # Check memory (minimum 512MB free)
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_memory" -lt 512 ]; then
        warning_to_file "$log_file" "Low memory detected. Available: ${available_memory}MB"
    else
        success_to_file "$log_file" "Sufficient memory available: ${available_memory}MB"
    fi
    
    # Check if required commands exist
    local required_commands=("git" "python3.11" "pip" "npm" "systemctl" "nginx" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error_to_file "$log_file" "Required command '$cmd' not found"
        fi
    done
    
    success_to_file "$log_file" "System resource checks passed"
}

# Port availability check
check_port_availability() {
    local port="$1"
    local log_file="${2:-/dev/null}"
    
    log "🔍 Checking port availability: $port"
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        error_to_file "$log_file" "Port $port is already in use"
    else
        success_to_file "$log_file" "Port $port is available"
    fi
}

# Configuration validation
validate_configuration_file() {
    local config_file="$1"
    local required_vars=("$@")
    local log_file="${required_vars[-1]}"
    
    # Remove log_file from required_vars if it's the last element
    if [[ "${required_vars[-1]}" == *".log" ]] || [[ "${required_vars[-1]}" == "/dev/null" ]]; then
        required_vars=("${required_vars[@]:0:$(( ${#required_vars[@]} - 1 ))}")
    fi
    
    log "🔍 Validating configuration file: $config_file"
    
    if [ ! -f "$config_file" ]; then
        error_to_file "$log_file" "Configuration file not found: $config_file"
    fi
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$config_file"; then
            error_to_file "$log_file" "Required configuration variable '$var' not found in $config_file"
        fi
    done
    
    success_to_file "$log_file" "Configuration file validation passed"
}

# Cleanup function for failed deployments
cleanup_failed_deployment() {
    local target_dir="$1"
    local service_names=("$2" "$3")
    local log_file="${4:-/dev/null}"
    
    log "🧹 Cleaning up failed deployment..."
    
    # Stop services
    for service in "${service_names[@]}"; do
        if [ -n "$service" ]; then
            stop_service_safely "$service" "$log_file" || true
        fi
    done
    
    # Remove temporary files
    if [ -d "$target_dir" ]; then
        warning_to_file "$log_file" "Target directory $target_dir exists but deployment failed"
    fi
    
    success_to_file "$log_file" "Cleanup completed"
}

# Export functions for use in other scripts
export -f log log_to_file error error_to_file warning warning_to_file success success_to_file
export -f health_check_endpoint check_service_status start_service_safely stop_service_safely
export -f create_database_backup git_update_repository install_dependencies_with_retry
export -f check_system_resources check_port_availability validate_configuration_file cleanup_failed_deployment
