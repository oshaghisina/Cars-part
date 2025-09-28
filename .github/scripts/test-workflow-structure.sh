#!/bin/bash

# Test Workflow Structure Validation
# Validates that all reusable actions and scripts are properly structured

set -e

echo "🔍 Testing Workflow Structure..."

# Check if all required files exist
REQUIRED_FILES=(
    ".github/actions/setup-environment/action.yml"
    ".github/actions/run-tests/action.yml"
    ".github/actions/build-frontend/action.yml"
    ".github/actions/manage-services/action.yml"
    ".github/actions/deploy/action.yml"
    ".github/scripts/check-parts-changes.sh"
    ".github/scripts/workflow-logging.sh"
    ".github/workflows/parts-deploy-pipeline.yml"
)

echo "📋 Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
        exit 1
    fi
done

# Check if scripts are executable
echo "🔧 Checking script permissions..."
SCRIPTS=(
    ".github/scripts/check-parts-changes.sh"
    ".github/scripts/workflow-logging.sh"
    ".github/scripts/test-workflow-structure.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script (executable)"
    else
        echo "❌ $script (not executable)"
        exit 1
    fi
done

# Validate YAML syntax for actions
echo "🔍 Validating YAML syntax..."
for action in .github/actions/*/action.yml; do
    if command -v yamllint >/dev/null 2>&1; then
        if yamllint "$action" >/dev/null 2>&1; then
            echo "✅ $action (valid YAML)"
        else
            echo "❌ $action (invalid YAML)"
            exit 1
        fi
    else
        echo "⚠️ yamllint not available, skipping YAML validation"
    fi
done

# Test conditional helper script
echo "🧪 Testing conditional helper script..."
if ./.github/scripts/check-parts-changes.sh >/dev/null 2>&1; then
    echo "✅ Parts change detection script works"
else
    echo "❌ Parts change detection script failed"
    exit 1
fi

# Test logging framework
echo "🧪 Testing logging framework..."
if ./.github/scripts/workflow-logging.sh >/dev/null 2>&1; then
    echo "✅ Logging framework works"
else
    echo "❌ Logging framework failed"
    exit 1
fi

echo "🎉 All workflow structure tests passed!"
echo "✅ Ready for Phase 4: Optimize Main CI/CD"
