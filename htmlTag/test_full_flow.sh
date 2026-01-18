#!/bin/bash
set -e

echo "🧪 Testing Full html.ai Flow"
echo "================================"
echo ""

# Check backend
echo "1. Testing backend..."
HEALTH=$(curl -s http://localhost:3000/ | jq -r '.status' 2>/dev/null || echo "error")
if [ "$HEALTH" = "running" ]; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not responding correctly"
    exit 1
fi

# Create test user
echo ""
echo "2. Creating test user..."
USER_ID="test_user_$(date +%s)"
RESPONSE=$(curl -s -X POST http://localhost:3000/api/user \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$USER_ID\",\"component_id\":\"test\",\"original_html\":\"<div>Test</div>\"}")

if echo "$RESPONSE" | grep -q "selected_variant"; then
    echo "   ✅ User created successfully"
    echo "   User ID: $USER_ID"
else
    echo "   ❌ Failed to create user"
    echo "   Response: $RESPONSE"
    exit 1
fi

# Send reward
echo ""
echo "3. Sending reward..."
REWARD_RESPONSE=$(curl -s -X POST http://localhost:3000/api/reward \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$USER_ID\",\"component_id\":\"test\",\"variant_id\":\"A\",\"reward_type\":\"click\",\"value\":1.0}")

if echo "$REWARD_RESPONSE" | grep -q "new_score"; then
    echo "   ✅ Reward tracked successfully"
else
    echo "   ❌ Failed to send reward"
    exit 1
fi

# Check dashboard data
echo ""
echo "4. Checking dashboard data..."
DASHBOARD=$(curl -s http://localhost:3000/api/users/all)
USER_COUNT=$(echo "$DASHBOARD" | jq -r '.total_users' 2>/dev/null || echo "0")

echo "   Total users in system: $USER_COUNT"
if [ "$USER_COUNT" -gt "0" ]; then
    echo "   ✅ Dashboard has user data"
else
    echo "   ❌ No users in dashboard"
    exit 1
fi

echo ""
echo "================================"
echo "✅ ALL TESTS PASSED!"
echo ""
echo "Now test manually:"
echo "1. Open: http://localhost:8082/demo-business-a.html"
echo "2. Click on products"
echo "3. Click 'Add to Cart' buttons"
echo "4. Click 'Visit FashionMart' link"
echo "5. See cross-site banner"
echo "6. Open dashboard: http://localhost:8082/dashboard.html"
echo "7. See your user with all events!"
echo ""

