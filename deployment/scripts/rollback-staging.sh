#!/bin/bash

# Staging Environment Rollback Script
# This script rolls back the staging environment to a previous deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_DIR="/opt/china-car-parts-staging"
VENV_DIR="$REPO_DIR/venv"
API_SERVICE="china-car-parts-api-staging"
BOT_SERVICE="china-car-parts-bot-staging"
BACKUP_DIR="/opt/backups/china-car-parts-staging"
LOG_FILE="/var/log/china-car-parts-staging-rollback.log"

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

# Show available backups
list_backups() {
    log "📋 Available backups:"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory $BACKUP_DIR does not exist"
    fi
    
    cd "$BACKUP_DIR"
    ls -la | grep "backup-" | awk '{print $9, $6, $7, $8}' | while read backup; do
        echo "  - $backup"
    done
    
    echo ""
    log "Latest backup: $(cat latest 2>/dev/null || echo 'None')"
}

# Rollback to specific backup
rollback_to_backup() {
    local backup_name="$1"
    
    if [ -z "$backup_name" ]; then
        error "Backup name is required"
    fi
    
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ ! -d "$backup_path" ]; then
        error "Backup $backup_name does not exist"
    fi
    
    log "🔄 Rolling back to backup: $backup_name"
    
    # Stop services
    log "⏹️ Stopping services..."
    systemctl stop $API_SERVICE || true
    systemctl stop $BOT_SERVICE || true
    
    # Wait for services to stop
    sleep 5
    
    # Create current state backup before rollback
    local current_backup="rollback-backup-$(date +%Y%m%d-%H%M%S)"
    log "📦 Creating backup of current state: $current_backup"
    
    if [ -d "$REPO_DIR" ]; then
        cp -r "$REPO_DIR" "$BACKUP_DIR/$current_backup"
    fi
    
    # Remove current deployment
    log "🗑️ Removing current deployment..."
    rm -rf "$REPO_DIR"
    
    # Restore from backup
    log "📥 Restoring from backup..."
    cp -r "$backup_path" "$REPO_DIR"
    
    # Set correct ownership
    chown -R partsbot:partsbot "$REPO_DIR"
    
    # Start services
    log "🚀 Starting services..."
    systemctl start $API_SERVICE
    systemctl start $BOT_SERVICE
    
    # Wait for services to start
    sleep 10
    
    # Verify services are running
    if systemctl is-active --quiet $API_SERVICE && systemctl is-active --quiet $BOT_SERVICE; then
        success "Services started successfully"
    else
        error "Failed to start services after rollback"
    fi
    
    # Update latest backup marker
    echo "$backup_name" > "$BACKUP_DIR/latest"
    
    success "✅ Rollback to $backup_name completed successfully"
}

# Rollback to latest backup
rollback_to_latest() {
    if [ ! -f "$BACKUP_DIR/latest" ]; then
        error "No latest backup marker found"
    fi
    
    local latest_backup=$(cat "$BACKUP_DIR/latest")
    rollback_to_backup "$latest_backup"
}

# Health check after rollback
health_check() {
    log "🩺 Running health checks after rollback..."
    
    # Wait for services to be ready
    sleep 15
    
    # Check API health
    local api_url="http://localhost:8001"
    for i in {1..10}; do
        if curl -f -s "$api_url/health" > /dev/null; then
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
    
    local api_errors=$(journalctl -u $API_SERVICE --since "5 minutes ago" | grep -i error | wc -l)
    if [ "$api_errors" -gt 0 ]; then
        warning "Found $api_errors errors in API service logs"
        journalctl -u $API_SERVICE --since "5 minutes ago" | grep -i error | tail -5
    fi
    
    local bot_errors=$(journalctl -u $BOT_SERVICE --since "5 minutes ago" | grep -i error | wc -l)
    if [ "$bot_errors" -gt 0 ]; then
        warning "Found $bot_errors errors in Bot service logs"
        journalctl -u $BOT_SERVICE --since "5 minutes ago" | grep -i error | tail -5
    fi
    
    success "Health checks completed"
}

# Interactive rollback
interactive_rollback() {
    log "🔍 Interactive rollback mode"
    
    list_backups
    
    echo ""
    read -p "Enter backup name to rollback to (or 'latest'): " backup_input
    
    if [ "$backup_input" = "latest" ]; then
        rollback_to_latest
    else
        rollback_to_backup "$backup_input"
    fi
    
    health_check
}

# Show help
show_help() {
    echo "Staging Environment Rollback Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -l, --list              List available backups"
    echo "  -b, --backup BACKUP     Rollback to specific backup"
    echo "  -L, --latest            Rollback to latest backup"
    echo "  -i, --interactive       Interactive rollback mode"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --list"
    echo "  $0 --backup backup-20240101-120000"
    echo "  $0 --latest"
    echo "  $0 --interactive"
}

# Main function
main() {
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    case "${1:-}" in
        -l|--list)
            list_backups
            ;;
        -b|--backup)
            if [ -z "${2:-}" ]; then
                error "Backup name is required with --backup option"
            fi
            rollback_to_backup "$2"
            health_check
            ;;
        -L|--latest)
            rollback_to_latest
            health_check
            ;;
        -i|--interactive)
            interactive_rollback
            ;;
        -h|--help)
            show_help
            ;;
        "")
            interactive_rollback
            ;;
        *)
            error "Unknown option: $1. Use --help for usage information."
            ;;
    esac
}

# Run main function
main "$@"
