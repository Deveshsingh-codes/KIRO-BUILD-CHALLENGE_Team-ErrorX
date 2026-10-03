#!/bin/bash

echo "=== FINAL UPLOAD VERIFICATION ==="

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: OK"

# Upload
echo "test" > /tmp/final_test.txt
RESULT=$(curl -s -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/final_test.txt" \
  -F "title=Final Test" \
  -F "description=Testing upload" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$RESULT" | grep "HTTP_CODE" | cut -d: -f2)
JSON=$(echo "$RESULT" | grep -v "HTTP_CODE")

echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "201" ]; then
    echo "✓ Upload successful!"
    echo "$JSON" | python3 -m json.tool | head -10
else
    echo "Upload response:"
    echo "$JSON"
fi
