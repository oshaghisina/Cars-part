#!/bin/bash

echo "🔄 Consolidating GitHub Actions Workflows..."

# Navigate to project directory
cd "$(dirname "$0")"

# Backup old workflows
echo "📦 Creating backup of old workflows..."
mkdir -p .github/workflows/backup
cp .github/workflows/ci.yml .github/workflows/backup/ 2>/dev/null || true
cp .github/workflows/security.yml .github/workflows/backup/ 2>/dev/null || true
cp .github/workflows/performance.yml .github/workflows/backup/ 2>/dev/null || true
cp .github/workflows/cd-staging.yml .github/workflows/backup/ 2>/dev/null || true
cp .github/workflows/cd-production.yml .github/workflows/backup/ 2>/dev/null || true

# Disable old workflows by renaming them
echo "🚫 Disabling old workflows..."
mv .github/workflows/ci.yml .github/workflows/ci.yml.disabled 2>/dev/null || true
mv .github/workflows/security.yml .github/workflows/security.yml.disabled 2>/dev/null || true
mv .github/workflows/performance.yml .github/workflows/performance.yml.disabled 2>/dev/null || true
mv .github/workflows/cd-staging.yml .github/workflows/cd-staging.yml.disabled 2>/dev/null || true
mv .github/workflows/cd-production.yml .github/workflows/cd-production.yml.disabled 2>/dev/null || true

# Keep dependencies workflow as it runs on schedule
echo "✅ Keeping dependencies.yml (runs on schedule)"

echo "🎉 Workflow consolidation complete!"
echo ""
echo "📋 Summary:"
echo "✅ New consolidated workflow: main.yml"
echo "🚫 Disabled old workflows: ci.yml, security.yml, performance.yml, cd-staging.yml, cd-production.yml"
echo "✅ Kept: dependencies.yml (scheduled runs)"
echo ""
echo "🚀 Next steps:"
echo "1. Commit and push these changes"
echo "2. Your next push will trigger only the new consolidated workflow"
echo "3. Monitor the new workflow in GitHub Actions"
echo ""
echo "💡 Benefits:"
echo "- Single workflow instead of 4 separate ones"
echo "- Parallel execution of all checks"
echo "- Cleaner GitHub Actions interface"
echo "- Better resource utilization"
echo "- Easier to monitor and debug"
