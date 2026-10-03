#!/bin/bash

TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "test" > /tmp/debug.txt

# Show what curl sends
echo "=== Curl sends ==="
curl -v -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/debug.txt" \
  -F "title=Debug Title" \
  -F "description=Debug Desc" 2>&1 | grep -E "(Content-Type|Content-Disposition|title|description)" | head -20
