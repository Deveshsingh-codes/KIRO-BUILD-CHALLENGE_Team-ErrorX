#!/bin/bash

echo "=== TESTING THE EXACT 422 SCENARIO THAT CAUSED BLACK SCREEN ==="

# Login first to get token
BASE_URL="http://localhost:8000"
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')

TOKEN=$(echo "$LOGIN" | jq -r '.access_token' 2>/dev/null)

echo "Testing what happens when backend returns 422 validation error..."
echo ""

# Try to trigger a 422 by sending malformed data
# (This is what was causing the React crash)
echo "Sending request that will trigger 422:"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}')

echo "$RESPONSE"
echo ""
echo "The response detail structure above is what React was trying to render."
echo "Our fix in Dashboard.tsx now:"
echo "  1. Checks if detail is an array"
echo "  2. Extracts .msg from each validation error object"
echo "  3. Joins them into a single string"
echo "  4. Falls back to JSON.stringify if needed"
echo ""
echo "This prevents the 'Objects are not valid as a React child' error."
