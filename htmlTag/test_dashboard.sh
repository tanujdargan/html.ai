#!/bin/bash

# Test script for dashboard and API

echo "=================================="
echo "Dashboard & API Test Script"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo "Please start Docker Desktop first"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if backend is running
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Backend is already running on port 3000"
else
    echo "Starting backend..."
    cd /Users/takatoshilee/html.ai/htmlTag
    docker compose up -d
    echo "Waiting for backend to start..."
    sleep 5
fi

echo ""
echo "Testing API endpoints..."
echo ""

# Test 1: Health check
echo "[Test 1] Health check..."
response=$(curl -s http://localhost:3000/)
if echo "$response" | grep -q "running"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test 2: Create test user
echo ""
echo "[Test 2] Creating test user..."
response=$(curl -s -X POST http://localhost:3000/tagAi \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "dashboard_test_user",
    "changingHtml": "<button>Test Button A</button>",
    "contextHtml": "<div>Test Context</div>"
  }')

if echo "$response" | grep -q "ok"; then
    echo "✅ Test user created"
else
    echo "❌ Failed to create test user"
    echo "Response: $response"
fi

# Test 3: Get all users
echo ""
echo "[Test 3] Fetching all users..."
response=$(curl -s http://localhost:3000/api/users/all)
if echo "$response" | grep -q "users"; then
    echo "✅ Users endpoint working"
    # Count users
    user_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['users']))" 2>/dev/null || echo "?")
    echo "   Found $user_count users"
else
    echo "❌ Users endpoint failed"
fi

# Test 4: Get user journey
echo ""
echo "[Test 4] Fetching user journey..."
response=$(curl -s http://localhost:3000/api/user/dashboard_test_user/journey)
if echo "$response" | grep -q "user_id"; then
    echo "✅ User journey endpoint working"
    # Check for variants
    if echo "$response" | grep -q "variants"; then
        echo "   ✅ Variants data present"
    fi
    if echo "$response" | grep -q "current_score"; then
        echo "   ✅ Scores present"
    fi
else
    echo "❌ User journey endpoint failed"
    echo "Response: $response"
fi

# Test 5: Dashboard analytics
echo ""
echo "[Test 5] Fetching dashboard analytics..."
response=$(curl -s http://localhost:3000/api/analytics/dashboard)
if echo "$response" | grep -q "total_users"; then
    echo "✅ Analytics endpoint working"
else
    echo "❌ Analytics endpoint failed"
fi

echo ""
echo "=================================="
echo "Testing Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Open dashboard: open /Users/takatoshilee/html.ai/htmlTag/dashboard.html"
echo "2. Click on 'dashboard_test_user' to see the modal"
echo "3. Check that you see:"
echo "   - Variant A and B scores"
echo "   - Side-by-side HTML previews"
echo "   - Version history"
echo ""
