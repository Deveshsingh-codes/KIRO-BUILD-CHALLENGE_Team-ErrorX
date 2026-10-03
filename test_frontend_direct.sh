#!/bin/bash

# Test what the frontend might be doing
echo "=== Simulating Frontend Behavior ==="

# Step 1: Login (this works)
echo "1. Login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}')
echo "Response: $RESPONSE"

TOKEN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"

# Step 2: Try GET /documents/ exactly as axios would
echo -e "\n2. GET /documents/ with axios-like headers..."
curl -v -X GET http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" 2>&1 | grep -E "(< HTTP|Authorization)"

# Step 3: Try POST /documents/upload with multipart
echo -e "\n3. POST /documents/upload with multipart..."
echo "test" > /tmp/test.txt
curl -v -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test.txt" 2>&1 | grep -E "(< HTTP|> Authorization)"
