#!/bin/bash
#
# CORS Smoke Test Script
# Tests asset serving, CORS preflight, and authentication flow for a given host
#
# Usage:
#   ./smoke_cors.sh HOST [USERNAME] [PASSWORD]
#   
# Environment Variables:
#   HOST        - Target host (required): http://5.223.41.154 or https://example.com
#   USERNAME    - Admin username for login test (optional)
#   PASSWORD    - Admin password for login test (optional)
#   ENDPOINTS   - Override default API endpoints (optional)
#   TIMEOUT     - Request timeout in seconds (default: 10)
#
# Examples:
#   ./smoke_cors.sh http://5.223.41.154
#   HOST=https://example.com USERNAME=admin PASSWORD=secret ./smoke_cors.sh
#

set -e  # Exit on error

# Configuration
TIMEOUT=${TIMEOUT:-10}
ENDPOINTS=${ENDPOINTS:-"/api/v1/users/login,/api/v1/users/me"}
LOGIN_ENDPOINT=$(echo "$ENDPOINTS" | cut -d',' -f1)
ME_ENDPOINT=$(echo "$ENDPOINTS" | cut -d',' -f2)

# Parse arguments
HOST=${1:-$HOST}
USERNAME=${2:-$USERNAME}
PASSWORD=${3:-$PASSWORD}

# Usage function
usage() {
    echo "Usage: $0 HOST [USERNAME] [PASSWORD]"
    echo ""
    echo "Arguments:"
    echo "  HOST        Target host (required): http://5.223.41.154"
    echo "  USERNAME    Admin username for login test (optional)"
    echo "  PASSWORD    Admin password for login test (optional)"
    echo ""
    echo "Environment Variables:"
    echo "  TIMEOUT     Request timeout in seconds (default: 10)"
    echo "  ENDPOINTS   Override API endpoints (default: /api/v1/users/login,/api/v1/users/me)"
    echo ""
    echo "Examples:"
    echo "  $0 http://5.223.41.154"
    echo "  HOST=https://example.com USERNAME=admin PASSWORD=secret $0"
    exit 1
}

# Validate HOST parameter
if [ -z "$HOST" ]; then
    echo "❌ ERROR: HOST parameter is required"
    echo ""
    usage
fi

# Helper functions
test_step() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "🧪 Testing $name... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo "✅ PASS"
        return 0
    else
        echo "❌ FAIL"
        echo "   Expected: $expected"
        return 1
    fi
}

test_step_verbose() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    echo "🧪 Testing $name..."
    echo "   Command: $command"
    
    local output
    output=$(eval "$command" 2>&1)
    local status=$?
    
    if [ $status -eq 0 ]; then
        echo "   ✅ PASS"
        return 0
    else
        echo "   ❌ FAIL"
        echo "   Expected: $expected"
        echo "   Output: $output"
        return 1
    fi
}

# Main test execution
echo "🚀 CORS Smoke Test Suite"
echo "========================"
echo "Target Host: $HOST"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if "$@"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test 1: Asset Serving
echo "📁 Testing Asset Serving"
echo "------------------------"
run_test test_step "Panel Index" \
    "curl -fsS -m $TIMEOUT -I '$HOST/panel/' | head -1 | grep -q '200 OK'" \
    "200 OK response"

run_test test_step "Vite Asset" \
    "curl -fsS -m $TIMEOUT -I '$HOST/panel/vite.svg' | head -1 | grep -q '200 OK'" \
    "200 OK response"

echo ""

# Test 2: CORS Preflight
echo "🌐 Testing CORS Preflight"
echo "-------------------------"
run_test test_step_verbose "OPTIONS Preflight" \
    "curl -fsS -m $TIMEOUT -X OPTIONS '$HOST$ME_ENDPOINT' \
        -H 'Origin: $HOST' \
        -H 'Access-Control-Request-Method: GET' \
        -H 'Access-Control-Request-Headers: Authorization, Content-Type' \
        | grep -q 'access-control-allow-origin'" \
    "200/204 with Access-Control-Allow-Origin header"

echo ""

# Test 3: Authentication Flow (if credentials provided)
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    echo "🔐 Testing Authentication Flow"
    echo "------------------------------"
    
    # Login test
    echo "🧪 Testing Login..."
    LOGIN_RESPONSE=$(curl -fsS -m $TIMEOUT -X POST "$HOST$LOGIN_ENDPOINT" \
        -H 'Content-Type: application/json' \
        -H "Origin: $HOST" \
        -d "{\"username_or_email\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" 2>/dev/null)
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo "   ✅ PASS - Login successful"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Extract token (basic extraction, works with jq or sed)
        if command -v jq >/dev/null 2>&1; then
            TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
        else
            TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
        fi
        
        if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
            # Test protected endpoint
            echo "🧪 Testing Protected Endpoint..."
            if curl -fsS -m $TIMEOUT -X GET "$HOST$ME_ENDPOINT" \
                -H "Authorization: Bearer $TOKEN" \
                -H "Origin: $HOST" >/dev/null 2>&1; then
                echo "   ✅ PASS - /users/me accessible"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo "   ❌ FAIL - /users/me request failed"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
        else
            echo "   ❌ FAIL - Could not extract access token"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo "   ❌ FAIL - Login request failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 2))
else
    echo "ℹ️  Skipping authentication tests (no credentials provided)"
fi

echo ""

# Summary
echo "📊 Test Results Summary"
echo "======================"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! CORS configuration is working correctly."
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please review the output above."
    echo ""
    echo "Common issues:"
    echo "- Asset 404: Check frontend deployment"
    echo "- CORS preflight failure: Verify backend CORS origins include $HOST"
    echo "- Login failure: Check credentials or backend configuration"
    exit 1
fi
