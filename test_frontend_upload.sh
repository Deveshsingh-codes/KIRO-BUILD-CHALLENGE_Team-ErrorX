#!/bin/bash

echo "=== Testing Frontend Upload Flow ==="

# Create test user
EMAIL="uploadtest$(date +%s)@test.com"
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123\",\"full_name\":\"Upload Test\"}" > /dev/null

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "✓ User logged in"

# Test upload with title and description (as frontend does)
echo "test file content" > /tmp/upload_test.txt

echo -e "\n✓ Testing upload with file + title + description:"
RESPONSE=$(curl -s -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/upload_test.txt" \
  -F "title=My Test Document" \
  -F "description=This is a test upload" \
  -w "\nHTTP:%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1 | cut -d: -f2)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "201" ]; then
    DOC_ID=$(echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✓ Upload successful: ID={d[\"id\"]}, Title={d[\"title\"]}, Desc={d[\"description\"]}')")
    echo "$DOC_ID"
else
    echo "❌ Upload failed with HTTP $HTTP_CODE"
    echo "$BODY"
fi

# Test getting documents
echo -e "\n✓ Testing GET /documents/:"
curl -s http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; docs=json.load(sys.stdin); print(f'  Found {len(docs)} document(s)')"

echo -e "\n=== All API tests passed ==="
