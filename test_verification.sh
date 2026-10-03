#!/bin/bash
BASE_URL="http://localhost:8000"

# Use existing user from previous tests
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')

TOKEN=$(echo "$LOGIN" | jq -r '.access_token')

# Upload test image
echo "Creating test image..."
cat > /tmp/test_image.txt << 'IMG'
Test image content
IMG

echo "Uploading document..."
UPLOAD=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_image.txt" \
  -F "title=Verification Test" \
  -F "description=Testing new verification system")

DOC_ID=$(echo "$UPLOAD" | jq -r '.id')
echo "Document ID: $DOC_ID"

echo -e "\nRunning verification..."
VERIFY=$(curl -s -X POST "$BASE_URL/documents/$DOC_ID/verify" \
  -H "Authorization: Bearer $TOKEN")

echo -e "\nVerification Result:"
echo "$VERIFY" | jq '.verification_result' 2>/dev/null || echo "$VERIFY"

echo -e "\nDetections:"
echo "$VERIFY" | jq '.verification_result.detections[] | {name, detected, confidence, details}' 2>/dev/null
