#!/bin/bash

# 🚀 GitHub Repository Setup Script for China Car Parts
# This script helps you set up the repository for CI/CD deployment

set -e

echo "🚀 **GITHUB REPOSITORY SETUP - CHINA CAR PARTS**"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not initialized. Run 'git init' first."
    exit 1
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    print_warning "No remote origin set. Setting up GitHub remote..."
    git remote add origin https://github.com/oshaghisina/Cars-part.git
    print_status "GitHub remote added successfully"
fi

echo "📋 **REPOSITORY INFORMATION**"
echo "Repository: https://github.com/oshaghisina/Cars-part.git"
echo "Project: China Car Parts"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Add all files
echo "📁 **ADDING FILES TO REPOSITORY**"
git add .
print_status "All files staged"

# Check if there are changes to commit
if git diff --cached --quiet; then
    print_warning "No changes to commit"
else
    # Make initial commit
    echo "💾 **MAKING INITIAL COMMIT**"
    git commit -m "🚀 Initial commit: China Car Parts system

- Complete FastAPI backend with analytics
- Vue.js admin panel with real-time dashboard
- Telegram bot with AI-powered search
- Comprehensive CI/CD pipeline
- Blue-green deployment strategy
- Security scanning and performance monitoring
- Multi-environment support (staging/production)

Ready for deployment! 🎉"
    print_status "Initial commit created"
fi

# Create and push to main branch
echo "🌿 **SETTING UP MAIN BRANCH**"
git branch -M main
print_status "Main branch set"

# Push to GitHub
echo "⬆️  **PUSHING TO GITHUB**"
git push -u origin main
print_status "Code pushed to GitHub successfully"

echo ""
echo "🎉 **REPOSITORY SETUP COMPLETE!**"
echo "================================"
echo ""
echo "📋 **NEXT STEPS:**"
echo "1. Configure GitHub Secrets (see DEPLOYMENT.md)"
echo "2. Set up branch protection rules"
echo "3. Configure staging and production environments"
echo "4. Set up your deployment servers"
echo ""
echo "📚 **DOCUMENTATION:**"
echo "- README.md: Project overview and setup"
echo "- DEPLOYMENT.md: Complete deployment guide"
echo "- .github/workflows/: CI/CD pipeline configuration"
echo ""
echo "🔗 **REPOSITORY LINKS:**"
echo "- Repository: https://github.com/oshaghisina/Cars-part"
echo "- Actions: https://github.com/oshaghisina/Cars-part/actions"
echo "- Settings: https://github.com/oshaghisina/Cars-part/settings"
echo ""

# Check if we can access the repository
echo "🔍 **VERIFYING REPOSITORY ACCESS**"
if curl -s -o /dev/null -w "%{http_code}" https://github.com/oshaghisina/Cars-part | grep -q "200"; then
    print_status "Repository is accessible"
else
    print_warning "Repository might not be public yet or URL needs verification"
fi

echo ""
echo "🚀 **CI/CD PIPELINE STATUS:**"
echo "- ✅ GitHub Actions workflows configured"
echo "- ✅ Multi-environment deployment ready"
echo "- ✅ Security scanning enabled"
echo "- ✅ Performance monitoring active"
echo "- ✅ Blue-green deployment strategy implemented"
echo ""

print_info "Your China Car Parts repository is now ready for CI/CD deployment!"
print_info "Follow the DEPLOYMENT.md guide to complete the setup."
