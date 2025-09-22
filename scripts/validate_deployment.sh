#!/bin/bash
# Enhanced Deployment Validation Script
# This script validates that all components are working correctly after deployment

set -e

echo "🔍 Starting comprehensive deployment validation..."
echo "=================================================="

# Configuration
API_BASE_URL="http://localhost"
ADMIN_PANEL_URL="$API_BASE_URL/panel/"
CUSTOMER_PORTAL_URL="$API_BASE_URL/"
API_HEALTH_URL="$API_BASE_URL/api/v1/health"
API_PARTS_URL="$API_BASE_URL/api/v1/parts/"
API_LEADS_URL="$API_BASE_URL/api/v1/leads/"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Function to check if a URL is accessible
check_url() {
    local url=$1
    local description=$2
    local timeout=${3:-10}
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        print_status "SUCCESS" "$description is accessible"
        return 0
    else
        print_status "ERROR" "$description is not accessible"
        return 1
    fi
}

# Function to check API response
check_api_response() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
    
    if [ "$response_code" = "$expected_status" ]; then
        print_status "SUCCESS" "$description returned status $response_code"
        return 0
    else
        print_status "ERROR" "$description returned status $response_code (expected $expected_status)"
        return 1
    fi
}

# Function to check service status
check_service() {
    local service_name=$1
    local description=$2
    
    if systemctl is-active --quiet "$service_name"; then
        print_status "SUCCESS" "$description is running"
        return 0
    else
        print_status "ERROR" "$description is not running"
        return 1
    fi
}

# Function to check file permissions
check_file_permissions() {
    local path=$1
    local description=$2
    
    if [ -d "$path" ]; then
        if [ -r "$path" ] && [ -x "$path" ]; then
            print_status "SUCCESS" "$description has correct permissions"
            return 0
        else
            print_status "ERROR" "$description has incorrect permissions"
            return 1
        fi
    else
        print_status "ERROR" "$description directory does not exist"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local db_path=$1
    local description=$2
    
    if [ -f "$db_path" ]; then
        if sqlite3 "$db_path" "SELECT 1;" > /dev/null 2>&1; then
            print_status "SUCCESS" "$description is accessible"
            return 0
        else
            print_status "ERROR" "$description is not accessible"
            return 1
        fi
    else
        print_status "ERROR" "$description file does not exist"
        return 1
    fi
}

# Initialize counters
total_checks=0
passed_checks=0
failed_checks=0

# Run all validation checks
echo ""
print_status "INFO" "Running validation checks..."

# 1. Service Status Checks
echo ""
echo "🔄 Service Status Checks:"
echo "------------------------"

check_service "nginx" "Nginx web server" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

# Check for API services (blue/green)
if systemctl is-active --quiet "china-car-parts-api-blue"; then
    check_service "china-car-parts-api-blue" "Blue API service" && ((passed_checks++)) || ((failed_checks++))
    ((total_checks++))
fi

if systemctl is-active --quiet "china-car-parts-api-green"; then
    check_service "china-car-parts-api-green" "Green API service" && ((passed_checks++)) || ((failed_checks++))
    ((total_checks++))
fi

if systemctl is-active --quiet "china-car-parts-bot-blue"; then
    check_service "china-car-parts-bot-blue" "Blue Bot service" && ((passed_checks++)) || ((failed_checks++))
    ((total_checks++))
fi

if systemctl is-active --quiet "china-car-parts-bot-green"; then
    check_service "china-car-parts-bot-green" "Green Bot service" && ((passed_checks++)) || ((failed_checks++))
    ((total_checks++))
fi

# 2. File System Checks
echo ""
echo "📁 File System Checks:"
echo "---------------------"

check_file_permissions "/opt/china-car-parts-blue/app/frontend/panel/dist" "Admin Panel build directory" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

check_file_permissions "/opt/china-car-parts-blue/app/frontend/web/dist" "Customer Portal build directory" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

# 3. Database Checks
echo ""
echo "🗄️ Database Checks:"
echo "------------------"

check_database "/opt/china-car-parts-blue/data/china_car_parts.db" "Blue environment database" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

if [ -f "/opt/china-car-parts-green/data/china_car_parts.db" ]; then
    check_database "/opt/china-car-parts-green/data/china_car_parts.db" "Green environment database" && ((passed_checks++)) || ((failed_checks++))
    ((total_checks++))
fi

# 4. Network Connectivity Checks
echo ""
echo "🌐 Network Connectivity Checks:"
echo "------------------------------"

check_url "$API_HEALTH_URL" "API Health endpoint" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

check_url "$CUSTOMER_PORTAL_URL" "Customer Portal" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

check_url "$ADMIN_PANEL_URL" "Admin Panel" && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

# 5. API Functionality Checks
echo ""
echo "🔌 API Functionality Checks:"
echo "---------------------------"

check_api_response "$API_HEALTH_URL" "API Health check" 200 && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

check_api_response "$API_PARTS_URL" "Parts API endpoint" 200 && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

check_api_response "$API_LEADS_URL" "Leads API endpoint" 200 && ((passed_checks++)) || ((failed_checks++))
((total_checks++))

# 6. Nginx Configuration Check
echo ""
echo "🌐 Nginx Configuration Check:"
echo "----------------------------"

if nginx -t > /dev/null 2>&1; then
    print_status "SUCCESS" "Nginx configuration is valid"
    ((passed_checks++))
else
    print_status "ERROR" "Nginx configuration is invalid"
    ((failed_checks++))
fi
((total_checks++))

# 7. Frontend Build Validation
echo ""
echo "🎨 Frontend Build Validation:"
echo "----------------------------"

if [ -f "/opt/china-car-parts-blue/app/frontend/panel/dist/index.html" ]; then
    print_status "SUCCESS" "Admin Panel index.html exists"
    ((passed_checks++))
else
    print_status "ERROR" "Admin Panel index.html missing"
    ((failed_checks++))
fi
((total_checks++))

if [ -f "/opt/china-car-parts-blue/app/frontend/web/dist/index.html" ]; then
    print_status "SUCCESS" "Customer Portal index.html exists"
    ((passed_checks++))
else
    print_status "ERROR" "Customer Portal index.html missing"
    ((failed_checks++))
fi
((total_checks++))

# Check for asset files
if [ -d "/opt/china-car-parts-blue/app/frontend/panel/dist/assets" ]; then
    print_status "SUCCESS" "Admin Panel assets directory exists"
    ((passed_checks++))
else
    print_status "WARNING" "Admin Panel assets directory missing"
    ((failed_checks++))
fi
((total_checks++))

if [ -d "/opt/china-car-parts-blue/app/frontend/web/dist/assets" ]; then
    print_status "SUCCESS" "Customer Portal assets directory exists"
    ((passed_checks++))
else
    print_status "WARNING" "Customer Portal assets directory missing"
    ((failed_checks++))
fi
((total_checks++))

# 8. Performance Checks
echo ""
echo "⚡ Performance Checks:"
echo "--------------------"

# Check API response time
api_response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$API_HEALTH_URL" 2>/dev/null || echo "999")
if (( $(echo "$api_response_time < 2.0" | bc -l) )); then
    print_status "SUCCESS" "API response time is acceptable (${api_response_time}s)"
    ((passed_checks++))
else
    print_status "WARNING" "API response time is slow (${api_response_time}s)"
    ((failed_checks++))
fi
((total_checks++))

# Summary
echo ""
echo "📊 Validation Summary:"
echo "====================="
echo "Total checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $failed_checks"

if [ $failed_checks -eq 0 ]; then
    print_status "SUCCESS" "All validation checks passed! Deployment is successful."
    exit 0
elif [ $failed_checks -le 2 ]; then
    print_status "WARNING" "Most validation checks passed. Some minor issues detected."
    exit 1
else
    print_status "ERROR" "Multiple validation checks failed. Deployment may have issues."
    exit 1
fi
