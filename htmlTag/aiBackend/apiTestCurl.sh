#!/bin/bash

API_URL="http://localhost:3000"

echo "=== Testing /tagAi ==="
curl -X POST "$API_URL/tagAi" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "user123",
           "html": "<div>Hello World Test Block</div>"
         }'

echo -e "\n\n=== Testing /rewardTag ==="
curl -X POST "$API_URL/rewardTag" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "user123",
           "reward": 0.87
         }'

echo -e "\n\nDone!"