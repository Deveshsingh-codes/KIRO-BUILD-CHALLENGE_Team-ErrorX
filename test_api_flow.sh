#!/bin/bash

echo "=== Testing Complete Flow ==="
BASE_URL="http://localhost:8000"
TEST_EMAIL="apitest$(date +%s)@example.com"

# 1. Register
echo -e "\n1. REGISTER USER"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"testpass123\",\"full_name\":\"Test User\"}")
echo "$REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"

# 2. Login
echo -e "\n2. LOGIN"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"testpass123\"}")
echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to get token"
  exit 1
fi
echo "Token obtained: ${TOKEN:0:20}..."

# 3. Get Documents (should return empty list)
echo -e "\n3. GET DOCUMENTS"
DOCS_RESPONSE=$(curl -s -X GET "$BASE_URL/documents/" \
  -H "Authorization: Bearer $TOKEN")
echo "$DOCS_RESPONSE" | jq '.' 2>/dev/null || echo "$DOCS_RESPONSE"

# 4. Upload Document
echo -e "\n4. UPLOAD DOCUMENT"
echo "Test document content for API flow" > /tmp/test_doc.pdf
UPLOAD_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_doc.pdf" \
  -F "title=Test Document" \
  -F "description=Test upload via API")
echo "$UPLOAD_RESPONSE"

# 5. Get Documents Again
echo -e "\n5. GET DOCUMENTS AFTER UPLOAD"
DOCS_AFTER=$(curl -s -X GET "$BASE_URL/documents/" \
  -H "Authorization: Bearer $TOKEN")
echo "$DOCS_AFTER" | jq '.' 2>/dev/null || echo "$DOCS_AFTER"

echo -e "\n=== Flow Test Complete ==="
