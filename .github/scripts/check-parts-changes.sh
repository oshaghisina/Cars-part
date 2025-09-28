#!/bin/bash

# Check if parts-related files have changed
# Returns 0 if parts changes detected, 1 if no parts changes

set -e

echo "🔍 Checking for parts-related changes..."

# Define parts-related file patterns
PARTS_PATTERNS=(
    "app/api/routers/parts_*.py"
    "app/services/parts_enhanced_service.py"
    "app/schemas/parts_schemas.py"
    "app/models/stock_models.py"
    "app/frontend/web/src/views/Search.vue"
    "app/frontend/web/src/components/pdp/BuyBox.vue"
    "app/frontend/web/src/services/api.js"
    "app/frontend/panel/src/views/Parts.vue"
    "app/frontend/panel/src/api/partsApi.js"
)

# Check if we're in a pull request context
if [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
    echo "📋 Pull request detected, checking changed files..."
    
    # Get changed files from PR
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)
else
    echo "📋 Push detected, checking changed files..."
    
    # Get changed files from push
    if [ -n "$GITHUB_SHA" ]; then
        CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)
    else
        echo "⚠️ No GITHUB_SHA found, assuming parts changes"
        exit 0
    fi
fi

echo "📄 Changed files:"
echo "$CHANGED_FILES"

# Check if any parts-related files changed
for pattern in "${PARTS_PATTERNS[@]}"; do
    if echo "$CHANGED_FILES" | grep -q "$pattern"; then
        echo "✅ Parts-related changes detected: $pattern"
        echo "🛡️ Parts guardrails will run"
        exit 0
    fi
done

echo "❌ No parts-related changes detected"
echo "⏭️ Skipping parts guardrails"
exit 1
