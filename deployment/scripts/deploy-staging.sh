#!/bin/bash

# 🚀 Staging Deployment Script
# This script deploys the application to the staging environment

set -e  # Exit on any error

# Configuration
STAGING_DIR="/opt/china-car-parts"
STAGING_USER="${STAGING_USER:-staging}"
STAGING_HOST="${STAGING_HOST:-staging.yourdomain.com}"
BRANCH="${BRANCH:-staging}"

echo "🚀 Starting staging deployment..."
echo "📁 Target: $STAGING_USER@$STAGING_HOST:$STAGING_DIR"
echo "🌿 Branch: $BRANCH"

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

# Main deployment process
main() {
    echo "📋 Pre-deployment checks..."
    
    # Check if staging directory exists
    if ! run_staging "test -d $STAGING_DIR"; then
        echo "❌ Staging directory $STAGING_DIR does not exist"
        exit 1
    fi
    
    echo "📥 Pulling latest code..."
    run_staging "cd $STAGING_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH"
    
    echo "🐍 Setting up Python environment..."
    run_staging "cd $STAGING_DIR && source venv/bin/activate && pip install -r requirements.txt"
    
    echo "🗄️ Running database migrations..."
    run_staging "cd $STAGING_DIR && source venv/bin/activate && alembic upgrade head"
    
    echo "📦 Building frontend..."
    run_staging "cd $STAGING_DIR/app/frontend/panel && npm ci && npm run build"
    
    echo "🔄 Restarting services..."
    
    # Stop services
    run_staging "sudo systemctl stop china-car-parts-api-staging || true"
    run_staging "sudo systemctl stop china-car-parts-bot-staging || true"
    
    # Start API service
    echo "🚀 Starting API service..."
    run_staging "sudo systemctl start china-car-parts-api-staging"
    check_service "china-car-parts-api-staging"
    
    # Start Bot service
    echo "🤖 Starting Bot service..."
    run_staging "sudo systemctl start china-car-parts-bot-staging"
    check_service "china-car-parts-bot-staging"
    
    # Reload Nginx
    echo "🌐 Reloading Nginx..."
    run_staging "sudo systemctl reload nginx"
    
    # Health check
    health_check
    
    echo "✅ Staging deployment completed successfully!"
    echo "🌐 Staging URL: https://staging.yourdomain.com"
    echo "📊 API Health: https://staging.yourdomain.com/api/v1/health"
}

# Error handling
trap 'echo "❌ Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"
