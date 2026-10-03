#!/bin/bash

echo "=== Testing Upload to Find 422 Cause ==="

# Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:30}..."

# Test 1: Upload with just file
echo -e "\n1. Upload with ONLY file (no title/description):"
echo "test content" > /tmp/test1.txt
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test1.txt" \
  -w "\nHTTP Status: %{http_code}\n" 2>&1 | tail -3

# Test 2: Upload with file and title as separate form fields
echo -e "\n2. Upload with file + title + description as form fields:"
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test1.txt" \
  -F "title=My Document" \
  -F "description=Test description" \
  -w "\nHTTP Status: %{http_code}\n" 2>&1 | tail -3

# Test 3: What the frontend might be sending
echo -e "\n3. Checking what the frontend sends..."
echo "Frontend uses FormData.append('file', file)"
echo "Frontend uses FormData.append('title', title)"
echo "Frontend uses FormData.append('description', description)"
