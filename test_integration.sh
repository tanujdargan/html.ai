#!/bin/bash

# Quick test script to verify everything works

echo "=================================="
echo "html.ai Integration Test"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if agents are copied
echo "[1/5] Checking agents..."
if [ -d "htmlTag/aiBackend/agents" ] && [ -f "htmlTag/aiBackend/agents/workflow.py" ]; then
    echo -e "${GREEN}✓${NC} Agents found"
else
    echo -e "${RED}✗${NC} Agents missing - run ./htmlTag/integrate.sh"
    exit 1
fi

# Test 2: Check if models are copied
echo "[2/5] Checking models..."
if [ -d "htmlTag/aiBackend/models" ] && [ -f "htmlTag/aiBackend/models/events.py" ]; then
    echo -e "${GREEN}✓${NC} Models found"
else
    echo -e "${RED}✗${NC} Models missing - run ./htmlTag/integrate.sh"
    exit 1
fi

# Test 3: Check if .env exists
echo "[3/5] Checking .env file..."
if [ -f "htmlTag/aiBackend/.env" ]; then
    echo -e "${GREEN}✓${NC} .env file found"
    if grep -q "GEMINI_API_KEY=" htmlTag/aiBackend/.env; then
        echo -e "${GREEN}✓${NC} GEMINI_API_KEY present"
    else
        echo -e "${YELLOW}⚠${NC}  GEMINI_API_KEY not found in .env"
    fi
else
    echo -e "${RED}✗${NC} .env file missing"
    echo "Create it: echo 'GEMINI_API_KEY=your_key' > htmlTag/aiBackend/.env"
    exit 1
fi

# Test 4: Check if SDK is updated
echo "[4/5] Checking SDK..."
if [ -f "htmlTag/sdk/src/AiOptimizeElement_v2.js" ]; then
    echo -e "${GREEN}✓${NC} AiOptimizeElement_v2.js found"
else
    echo -e "${RED}✗${NC} AiOptimizeElement_v2.js missing"
    exit 1
fi

if grep -q "AiOptimizeElement_v2.js" htmlTag/sdk/src/index.js; then
    echo -e "${GREEN}✓${NC} index.js loads v2 SDK"
else
    echo -e "${YELLOW}⚠${NC}  index.js might not be loading v2 SDK"
fi

# Test 5: Check if Docker is running
echo "[5/5] Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running - start Docker Desktop"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}✓ All checks passed!${NC}"
echo "=================================="
echo ""
echo "Ready to test. Run:"
echo ""
echo "  Terminal 1: cd htmlTag && docker compose up --build"
echo "  Terminal 2: cd htmlTag/sdk/src && python3 -m http.server 8080"
echo "  Browser:    http://localhost:8080"
echo ""
echo "Check console for agent communication logs!"
echo ""
