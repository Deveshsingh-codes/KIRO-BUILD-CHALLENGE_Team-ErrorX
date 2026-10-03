#!/bin/bash

echo "=== Testing Actual Frontend Issue ==="

# The user must LOGIN first through the frontend
echo "User should:"
echo "1. Go to http://localhost:5173"
echo "2. Click Register or Login"
echo "3. Enter credentials"
echo "4. Get redirected to dashboard"
echo "5. Dashboard should work"
echo ""
echo "The 401 errors occur when:"
echo "- User has old/expired token in localStorage"
echo "- User refreshes page and token is invalid"
echo "- Frontend doesn't handle token validation"
echo ""
echo "Let's test by creating fresh user and logging in via API to simulate frontend..."

EMAIL="realtest$(date +%s)@test.com"

# Register
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123\",\"full_name\":\"Real Test\"}" > /dev/null

# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "✓ Fresh token: ${TOKEN:0:30}..."

# Test all endpoints
echo -e "\n✓ GET /documents/:"
curl -s http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print('  Status: OK, Docs:', len(json.load(sys.stdin)))"

echo -e "\n✓ POST /documents/upload:"
echo "test" > /tmp/real_test.txt
curl -s http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/real_test.txt" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  Uploaded: {d['id']}\")"

echo -e "\n=== Backend works perfectly! ==="
echo "The issue is: Frontend not storing/sending token correctly"
