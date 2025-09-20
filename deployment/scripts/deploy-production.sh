#!/bin/bash

# 🚀 Production Deployment Script
# This script deploys the application to the production environment with safety measures

set -e  # Exit on any error

# Configuration
PROD_DIR="/opt/china-car-parts"
PROD_USER="${PROD_USER:-production}"
PROD_HOST="${PROD_HOST:-yourdomain.com}"
BRANCH="${BRANCH:-main}"
BACKUP_DIR="/backup/china-car-parts"

echo "🚀 Starting PRODUCTION deployment..."
echo "📁 Target: $PROD_USER@$PROD_HOST:$PROD_DIR"
echo "🌿 Branch: $BRANCH"
echo "⚠️  PRODUCTION DEPLOYMENT - Proceed with caution!"

# Function to execute commands on production server
run_production() {
    ssh -o StrictHostKeyChecking=no "$PROD_USER@$PROD_HOST" "$@"
}

# Function to create database backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/china_car_parts_$timestamp.sql"
    
    echo "💾 Creating database backup..."
    
    run_production "mkdir -p $BACKUP_DIR"
    run_production "pg_dump china_car_parts > $backup_file"
    run_production "gzip $backup_file"
    
    echo "✅ Database backup created: ${backup_file}.gz"
    
    # Keep only last 10 backups
    run_production "ls -t $BACKUP_DIR/*.gz | tail -n +11 | xargs -r rm"
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service_name service..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_production "systemctl is-active --quiet $service_name"; then
            echo "✅ $service_name is running"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to run health check
health_check() {
    local max_attempts=15
    local attempt=1
    local api_url="${PROD_API_URL:-https://yourdomain.com}"
    
    echo "🏥 Running production health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if run_production "curl -f -s $api_url/api/v1/health > /dev/null"; then
            echo "✅ Production health check passed"
            return 0
        fi
        
        echo "⏳ Health check attempt $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ Production health check failed after $max_attempts attempts"
    return 1
}

# Function to rollback deployment
rollback() {
    echo "🔄 Starting rollback procedure..."
    
    # Stop current services
    run_production "sudo systemctl stop china-car-parts-api || true"
    run_production "sudo systemctl stop china-car-parts-bot || true"
    
    # Restore from backup (if needed)
    echo "📦 Rollback completed - manual intervention may be required"
    echo "🔗 Check logs: journalctl -u china-car-parts-api -f"
}

# Main deployment process
main() {
    echo "📋 Pre-deployment checks..."
    
    # Check if production directory exists
    if ! run_production "test -d $PROD_DIR"; then
        echo "❌ Production directory $PROD_DIR does not exist"
        exit 1
    fi
    
    # Create backup before deployment
    create_backup
    
    echo "📥 Pulling latest code..."
    run_production "cd $PROD_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH"
    
    echo "🐍 Setting up Python environment..."
    run_production "cd $PROD_DIR && source venv/bin/activate && pip install -r requirements.txt"
    
    echo "🗄️ Running database migrations..."
    run_production "cd $PROD_DIR && source venv/bin/activate && alembic upgrade head"
    
    echo "📦 Building frontend..."
    run_production "cd $PROD_DIR/app/frontend/panel && npm ci && npm run build"
    
    echo "🔄 Restarting services..."
    
    # Stop services gracefully
    echo "⏹️ Stopping services..."
    run_production "sudo systemctl stop china-car-parts-api || true"
    run_production "sudo systemctl stop china-car-parts-bot || true"
    
    # Wait for services to stop
    sleep 5
    
    # Start API service
    echo "🚀 Starting API service..."
    run_production "sudo systemctl start china-car-parts-api"
    check_service "china-car-parts-api"
    
    # Start Bot service
    echo "🤖 Starting Bot service..."
    run_production "sudo systemctl start china-car-parts-bot"
    check_service "china-car-parts-bot"
    
    # Reload Nginx
    echo "🌐 Reloading Nginx..."
    run_production "sudo systemctl reload nginx"
    
    # Wait for services to stabilize
    echo "⏳ Waiting for services to stabilize..."
    sleep 30
    
    # Health check
    health_check
    
    echo "✅ Production deployment completed successfully!"
    echo "🌐 Production URL: https://yourdomain.com"
    echo "📊 API Health: https://yourdomain.com/api/v1/health"
    echo "📈 Monitor logs: journalctl -u china-car-parts-api -f"
}

# Error handling with rollback
trap 'echo "❌ Production deployment failed at line $LINENO"; rollback; exit 1' ERR

# Confirmation prompt (for manual runs)
if [ "${SKIP_CONFIRMATION:-false}" != "true" ]; then
    echo "⚠️  WARNING: This will deploy to PRODUCTION!"
    echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
    sleep 10
fi

# Run main function
main "$@"
