#!/bin/bash

# Integration Script: Merge root project into htmlTag
# This copies the multi-agent backend into htmlTag structure

set -e  # Exit on error

echo "=================================="
echo "html.ai Integration Script"
echo "Merging root backend into htmlTag"
echo "=================================="

# Check we're in the right directory
if [ ! -d "htmlTag" ] || [ ! -d "backend" ]; then
    echo "ERROR: Please run this from html.ai/ root directory"
    exit 1
fi

echo ""
echo "[1/6] Creating directories..."
mkdir -p htmlTag/aiBackend/agents
mkdir -p htmlTag/aiBackend/models

echo "[2/6] Copying agent files..."
cp backend/agents/workflow.py htmlTag/aiBackend/agents/
cp backend/agents/analytics_agent.py htmlTag/aiBackend/agents/
cp backend/agents/identity_agent.py htmlTag/aiBackend/agents/
cp backend/agents/decision_agent.py htmlTag/aiBackend/agents/
cp backend/agents/guardrail_agent.py htmlTag/aiBackend/agents/
echo "  ✓ Copied 5 agent files"

echo "[3/6] Copying model files..."
cp backend/models/events.py htmlTag/aiBackend/models/
cp backend/models/variants.py htmlTag/aiBackend/models/
echo "  ✓ Copied 2 model files"

echo "[4/6] Creating __init__.py files..."
touch htmlTag/aiBackend/agents/__init__.py
touch htmlTag/aiBackend/models/__init__.py

echo "[5/6] Updating requirements.txt..."
cp htmlTag/aiBackend/requirements_integrated.txt htmlTag/aiBackend/requirements.txt
echo "  ✓ Updated requirements.txt"

echo "[6/6] Updating SDK..."
cd htmlTag/sdk/src
if [ ! -f "AiOptimizeElement_v2.js" ]; then
    echo "  ERROR: AiOptimizeElement_v2.js not found"
    exit 1
fi

# Update index.js to load v2
cat > index.js << 'EOF'
/**
 * AI Optimize SDK - v2.0
 * Load the custom element
 */
import './AiOptimizeElement_v2.js';
EOF

cd ../../..
echo "  ✓ Updated SDK to v2"

echo ""
echo "=================================="
echo "✓ Integration Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Add GEMINI_API_KEY to htmlTag/aiBackend/.env"
echo "2. Run: cd htmlTag && docker compose up --build"
echo "3. Open: http://localhost:8080"
echo ""
echo "Check INTEGRATION_GUIDE.md for full instructions"
echo ""
