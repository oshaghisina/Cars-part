#!/bin/bash

# 🚀 Dual SPA Deployment Test Script
# Tests the dual SPA architecture deployment readiness

set -e

echo "🚀 Starting Dual SPA Deployment Test"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test functions
test_build() {
    echo -e "\n${BLUE}📦 Testing Build Process${NC}"
    
    # Test Admin Panel build
    echo "Building Admin Panel..."
    cd app/frontend/panel
    npm run build:panel
    if [ -f "dist/index.html" ]; then
        echo -e "${GREEN}✅ Admin Panel build successful${NC}"
    else
        echo -e "${RED}❌ Admin Panel build failed${NC}"
        exit 1
    fi
    
    # Test Customer Portal build
    echo "Building Customer Portal..."
    cd ../web
    npm run build
    if [ -f "dist/index.html" ]; then
        echo -e "${GREEN}✅ Customer Portal build successful${NC}"
    else
        echo -e "${RED}❌ Customer Portal build failed${NC}"
        exit 1
    fi
    
    cd ../../..
}

test_asset_paths() {
    echo -e "\n${BLUE}🔍 Testing Asset Paths${NC}"
    
    # Check Admin Panel assets have /panel/ prefix
    if grep -q "/panel/assets/" app/frontend/panel/dist/index.html; then
        echo -e "${GREEN}✅ Admin Panel assets correctly prefixed with /panel/${NC}"
    else
        echo -e "${RED}❌ Admin Panel assets missing /panel/ prefix${NC}"
        exit 1
    fi
    
    # Check Customer Portal assets have / prefix
    if grep -q "/assets/" app/frontend/web/dist/index.html; then
        echo -e "${GREEN}✅ Customer Portal assets correctly prefixed with /${NC}"
    else
        echo -e "${RED}❌ Customer Portal assets missing / prefix${NC}"
        exit 1
    fi
}

test_nginx_config() {
    echo -e "\n${BLUE}🌐 Testing Nginx Configuration${NC}"
    
    # Check production config
    if grep -q "location /panel/" deployment/configs/nginx-production.conf; then
        echo -e "${GREEN}✅ Production Nginx config has /panel/ location${NC}"
    else
        echo -e "${RED}❌ Production Nginx config missing /panel/ location${NC}"
        exit 1
    fi
    
    if grep -q "location / {" deployment/configs/nginx-production.conf; then
        echo -e "${GREEN}✅ Production Nginx config has / location${NC}"
    else
        echo -e "${RED}❌ Production Nginx config missing / location${NC}"
        exit 1
    fi
    
    # Check staging config
    if grep -q "location /panel/" deployment/configs/nginx-staging.conf; then
        echo -e "${GREEN}✅ Staging Nginx config has /panel/ location${NC}"
    else
        echo -e "${RED}❌ Staging Nginx config missing /panel/ location${NC}"
        exit 1
    fi
}

test_ci_workflow() {
    echo -e "\n${BLUE}🔄 Testing CI/CD Workflow${NC}"
    
    # Check if workflow has frontend build steps
    if grep -q "Build Frontend" .github/workflows/main_password_auth.yml; then
        echo -e "${GREEN}✅ CI workflow has frontend build step${NC}"
    else
        echo -e "${RED}❌ CI workflow missing frontend build step${NC}"
        exit 1
    fi
    
    if grep -q "build:panel" .github/workflows/main_password_auth.yml; then
        echo -e "${GREEN}✅ CI workflow uses build:panel script${NC}"
    else
        echo -e "${RED}❌ CI workflow missing build:panel script${NC}"
        exit 1
    fi
}

test_api_health() {
    echo -e "\n${BLUE}🏥 Testing API Health${NC}"
    
    # Check if API is running
    if curl -s http://localhost:8001/api/v1/health > /dev/null; then
        echo -e "${GREEN}✅ API is running and healthy${NC}"
    else
        echo -e "${YELLOW}⚠️ API not running locally (expected for deployment test)${NC}"
    fi
}

test_file_structure() {
    echo -e "\n${BLUE}📁 Testing File Structure${NC}"
    
    # Check required directories exist
    required_dirs=(
        "app/frontend/panel/dist"
        "app/frontend/web/dist"
        "deployment/configs"
        ".github/workflows"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✅ Directory exists: $dir${NC}"
        else
            echo -e "${RED}❌ Missing directory: $dir${NC}"
            exit 1
        fi
    done
}

# Run all tests
echo -e "\n${BLUE}🧪 Running Deployment Tests${NC}"
echo "================================"

test_file_structure
test_build
test_asset_paths
test_nginx_config
test_ci_workflow
test_api_health

echo -e "\n${GREEN}🎉 All Deployment Tests Passed!${NC}"
echo -e "${GREEN}✅ Dual SPA architecture is ready for deployment${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Checklist:${NC}"
echo "  ✅ Admin Panel builds with /panel/ base path"
echo "  ✅ Customer Portal builds with / base path"
echo "  ✅ Nginx configs updated for dual SPAs"
echo "  ✅ CI/CD workflow includes frontend builds"
echo "  ✅ File structure is complete"
echo ""
echo -e "${YELLOW}🚀 Ready to deploy to staging/production!${NC}"
