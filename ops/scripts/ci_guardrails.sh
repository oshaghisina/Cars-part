#!/bin/bash
#
# CI CORS Guardrails Script
# Validates frontend builds and CORS configuration to prevent regressions
#
# Usage:
#   ./ci_guardrails.sh HOST [DIST_DIR]
#   
# Environment Variables:
#   HOST        - Target host (required): http://5.223.41.154
#   DIST_DIR    - Frontend dist directory (default: app/frontend/panel/dist)
#   STRICT      - Set to '1' for strict mode (exit on any warning)
#   TIMEOUT     - Request timeout in seconds (default: 10)
#
# Examples:
#   ./ci_guardrails.sh http://5.223.41.154
#   HOST=https://example.com DIST_DIR=dist ./ci_guardrails.sh
#   STRICT=1 ./ci_guardrails.sh http://5.223.41.154
#

# Configuration
TIMEOUT=${TIMEOUT:-10}
STRICT=${STRICT:-0}

# Parse arguments
HOST=${1:-$HOST}
DIST_DIR=${2:-${DIST_DIR:-"app/frontend/panel/dist"}}

# Colors for output (if terminal supports)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Usage function
usage() {
    echo "Usage: $0 HOST [DIST_DIR]"
    echo ""
    echo "Arguments:"
    echo "  HOST        Target host (required): http://5.223.41.154"
    echo "  DIST_DIR    Frontend dist directory (default: app/frontend/panel/dist)"
    echo ""
    echo "Environment Variables:"
    echo "  STRICT      Set to '1' for strict mode (exit on warnings)"
    echo "  TIMEOUT     Request timeout in seconds (default: 10)"
    echo ""
    echo "Examples:"
    echo "  $0 http://5.223.41.154"
    echo "  DIST_DIR=dist $0 https://example.com"
    echo "  STRICT=1 $0 http://5.223.41.154"
    exit 1
}

# Validate required parameters
if [ -z "$HOST" ]; then
    echo -e "${RED}❌ ERROR: HOST parameter is required${NC}"
    echo ""
    usage
fi

if [ ! -d "$DIST_DIR" ]; then
    echo -e "${RED}❌ ERROR: Distribution directory '$DIST_DIR' not found${NC}"
    echo "   Build the frontend first or check DIST_DIR path"
    exit 1
fi

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    if [ "$STRICT" = "1" ]; then
        exit 1
    fi
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}🔍 $1${NC}"
}

# Test execution tracking
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

run_check() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if "$@"; then
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

# Main execution
echo "🛡️  CI CORS Guardrails"
echo "===================="
echo "Target Host: $HOST"
echo "Dist Directory: $DIST_DIR"
echo "Strict Mode: $([ "$STRICT" = "1" ] && echo "ON" || echo "OFF")"
echo ""

# Check 1: Frontend Bundle Validation
log_step "Checking frontend bundles for hardcoded URLs"

# Check for hardcoded localhost API URLs (excluding source maps)
LOCALHOST_REFS=$(grep -r '"http://localhost:8001' "$DIST_DIR/" 2>/dev/null | grep -v '\.map' || true)

if [ -n "$LOCALHOST_REFS" ]; then
    log_error "Found hardcoded localhost URLs in production build:"
    echo "$LOCALHOST_REFS" | sed 's/^/     /'
    run_check false
else
    log_success "No hardcoded localhost URLs found in bundles"
    run_check true
fi

# Check for relative API paths (should be present)
RELATIVE_REFS=$(grep -r '/api/v1' "$DIST_DIR/" 2>/dev/null | grep -v '\.map' | head -3 || true)

if [ -n "$RELATIVE_REFS" ]; then
    log_success "Frontend using relative API paths"
    run_check true
else
    log_warning "No relative /api/v1 paths found in bundles"
    echo "   This might indicate a build issue"
    run_check false
fi

echo ""

# Check 2: CORS Preflight Validation
log_step "Testing CORS preflight configuration"

# Test OPTIONS request with production origin
CORS_TEST_CMD="curl -fsS -m $TIMEOUT -X OPTIONS '$HOST/api/v1/users/me' \
    -H 'Origin: $HOST' \
    -H 'Access-Control-Request-Method: GET' \
    -H 'Access-Control-Request-Headers: Authorization, Content-Type'"

if eval "$CORS_TEST_CMD" | grep -q "access-control-allow-origin"; then
    log_success "CORS preflight succeeds with correct headers"
    run_check true
else
    log_error "CORS preflight failed or missing headers"
    echo "   Command: $CORS_TEST_CMD"
    echo "   Expected: Response with 'access-control-allow-origin' header"
    run_check false
fi

echo ""

# Check 3: Asset Serving Validation
log_step "Testing asset serving"

if curl -fsS -m $TIMEOUT -I "$HOST/panel/vite.svg" | head -1 | grep -q "200 OK"; then
    log_success "Panel assets accessible"
    run_check true
else
    log_warning "Panel asset test failed"
    echo "   This might indicate frontend deployment issue"
    run_check false
fi

echo ""

# Optional Check 4: Authentication Flow (if credentials provided)
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    log_step "Testing authentication flow"
    
    # Attempt login
    LOGIN_CMD="curl -fsS -m $TIMEOUT -X POST '$HOST$LOGIN_ENDPOINT' \
        -H 'Content-Type: application/json' \
        -H 'Origin: $HOST' \
        -d '{\"username_or_email\":\"$USERNAME\",\"password\":\"$PASSWORD\"}'"
    
    LOGIN_RESPONSE=$(eval "$LOGIN_CMD" 2>/dev/null || echo "")
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        log_success "Login request succeeds"
        run_check true
        
        # Extract token for protected endpoint test
        if command -v jq >/dev/null 2>&1; then
            TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null || echo "")
        else
            TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p' 2>/dev/null || echo "")
        fi
        
        if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
            # Test protected endpoint
            ME_CMD="curl -fsS -m $TIMEOUT -X GET '$HOST$ME_ENDPOINT' \
                -H 'Authorization: Bearer $TOKEN' \
                -H 'Origin: $HOST'"
            
            if eval "$ME_CMD" >/dev/null 2>&1; then
                log_success "Protected endpoint accessible with token"
                run_check true
            else
                log_error "Protected endpoint test failed"
                run_check false
            fi
        else
            log_warning "Could not extract access token from login response"
            run_check false
        fi
    else
        log_error "Login request failed"
        echo "   Check credentials and backend configuration"
        run_check false
    fi
else
    log_info "Skipping authentication tests (no credentials provided)"
    echo "   Set USERNAME and PASSWORD environment variables to test auth flow"
fi

echo ""

# Summary
echo "📊 Guardrails Summary"
echo "===================="
echo "Total Checks: $CHECKS_TOTAL"
echo "Passed: $CHECKS_PASSED"
echo "Failed: $CHECKS_FAILED"
if [ $WARNINGS -gt 0 ]; then
    echo "Warnings: $WARNINGS"
fi

echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    log_success "All critical checks passed!"
    echo ""
    echo "🎯 System appears ready for production deployment"
    exit 0
else
    log_error "Some checks failed - deployment may have issues"
    echo ""
    echo "🔧 Recommended actions:"
    if grep -q "hardcoded localhost URLs" <<< "$LOCALHOST_REFS"; then
        echo "   - Rebuild frontend with VITE_API_BASE_URL=/api/v1"
    fi
    echo "   - Verify backend CORS configuration includes $HOST"
    echo "   - Check frontend asset deployment"
    echo "   - Review backend logs for CORS errors"
    exit 1
fi
