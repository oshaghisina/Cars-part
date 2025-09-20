#!/bin/bash

# 🏥 Health Check Script
# Comprehensive health checking for all environments

set -e

# Configuration
ENVIRONMENT="${ENVIRONMENT:-development}"
API_URL="${API_URL:-http://localhost:8001}"
MAX_RETRIES="${MAX_RETRIES:-5}"
RETRY_DELAY="${RETRY_DELAY:-10}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 Starting health check for $ENVIRONMENT environment${NC}"
echo -e "${BLUE}🔗 API URL: $API_URL${NC}"

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -e "${YELLOW}🔍 Checking $description...${NC}"
    
    local response_code
    local response_time
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo -e "   Attempt $attempt/$MAX_RETRIES: $url"
        
        # Get response code and time
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$url" || echo "000")
        response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 30 "$url" || echo "timeout")
        
        if [ "$response_code" = "$expected_status" ]; then
            echo -e "   ${GREEN}✅ $description: OK (${response_code}) - ${response_time}s${NC}"
            return 0
        else
            echo -e "   ${RED}❌ $description: Failed (${response_code}) - ${response_time}s${NC}"
        fi
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo -e "   ${YELLOW}⏳ Waiting $RETRY_DELAY seconds before retry...${NC}"
            sleep $RETRY_DELAY
        fi
        
        ((attempt++))
    done
    
    echo -e "   ${RED}❌ $description: FAILED after $MAX_RETRIES attempts${NC}"
    return 1
}

# Function to check service status (for production)
check_service() {
    local service_name=$1
    local description=$2
    
    echo -e "${YELLOW}🔍 Checking $description service...${NC}"
    
    if systemctl is-active --quiet "$service_name"; then
        echo -e "   ${GREEN}✅ $description service: Running${NC}"
        
        # Check if service is enabled
        if systemctl is-enabled --quiet "$service_name"; then
            echo -e "   ${GREEN}✅ $description service: Enabled${NC}"
        else
            echo -e "   ${YELLOW}⚠️ $description service: Running but not enabled${NC}"
        fi
        
        return 0
    else
        echo -e "   ${RED}❌ $description service: Not running${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    echo -e "${YELLOW}🔍 Checking database connection...${NC}"
    
    # Try to run a simple database query
    if python3 -c "
import os
import sys
sys.path.append('.')

try:
    from app.db.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ Database: Connected${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Database: Connection failed${NC}"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    echo -e "${YELLOW}🔍 Checking disk space...${NC}"
    
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        echo -e "   ${GREEN}✅ Disk space: OK (${usage}% used)${NC}"
        return 0
    elif [ "$usage" -lt 90 ]; then
        echo -e "   ${YELLOW}⚠️ Disk space: Warning (${usage}% used)${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Disk space: Critical (${usage}% used)${NC}"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    echo -e "${YELLOW}🔍 Checking memory usage...${NC}"
    
    local mem_info=$(free | grep Mem)
    local total=$(echo $mem_info | awk '{print $2}')
    local used=$(echo $mem_info | awk '{print $3}')
    local usage=$((used * 100 / total))
    
    if [ "$usage" -lt 80 ]; then
        echo -e "   ${GREEN}✅ Memory: OK (${usage}% used)${NC}"
        return 0
    elif [ "$usage" -lt 90 ]; then
        echo -e "   ${YELLOW}⚠️ Memory: Warning (${usage}% used)${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Memory: Critical (${usage}% used)${NC}"
        return 1
    fi
}

# Function to check logs for errors
check_logs() {
    echo -e "${YELLOW}🔍 Checking recent error logs...${NC}"
    
    local error_count=0
    
    # Check systemd service logs for errors in last 10 minutes
    if command -v journalctl >/dev/null 2>&1; then
        error_count=$(journalctl --since "10 minutes ago" --priority=err --no-pager | wc -l)
        
        if [ "$error_count" -eq 0 ]; then
            echo -e "   ${GREEN}✅ System logs: No recent errors${NC}"
        else
            echo -e "   ${YELLOW}⚠️ System logs: $error_count errors in last 10 minutes${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️ System logs: journalctl not available${NC}"
    fi
    
    return 0
}

# Main health check function
main() {
    local overall_status=0
    
    echo -e "\n${BLUE}📋 Running comprehensive health checks...${NC}\n"
    
    # API Health Check
    check_endpoint "$API_URL/health" "API Health Endpoint" || overall_status=1
    
    # API Documentation (if available)
    check_endpoint "$API_URL/docs" "API Documentation" || true  # Non-critical
    
    # Database Check
    if [ "$ENVIRONMENT" != "development" ]; then
        check_database || overall_status=1
    fi
    
    # System Resource Checks (production only)
    if [ "$ENVIRONMENT" = "production" ]; then
        check_disk_space || overall_status=1
        check_memory || overall_status=1
        check_logs
        
        # Service Status Checks
        check_service "china-car-parts-api" "API" || overall_status=1
        check_service "china-car-parts-bot" "Bot" || overall_status=1
        check_service "nginx" "Nginx" || overall_status=1
    fi
    
    # Summary
    echo -e "\n${BLUE}📊 Health Check Summary${NC}"
    echo -e "${BLUE}========================${NC}"
    
    if [ $overall_status -eq 0 ]; then
        echo -e "${GREEN}✅ All health checks passed!${NC}"
        echo -e "${GREEN}🚀 System is healthy and ready${NC}"
    else
        echo -e "${RED}❌ Some health checks failed${NC}"
        echo -e "${RED}⚠️ System may need attention${NC}"
    fi
    
    echo -e "\n${BLUE}📅 Check completed at: $(date)${NC}"
    
    return $overall_status
}

# Help function
show_help() {
    echo "🏥 Health Check Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment (development|staging|production)"
    echo "  -u, --url URL           API base URL"
    echo "  -r, --retries NUM       Max retry attempts (default: 5)"
    echo "  -d, --delay SECONDS     Delay between retries (default: 10)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Check development"
    echo "  $0 -e production -u https://api.example.com"
    echo "  $0 -e staging -r 3 -d 5"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -u|--url)
            API_URL="$2"
            shift 2
            ;;
        -r|--retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        -d|--delay)
            RETRY_DELAY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
