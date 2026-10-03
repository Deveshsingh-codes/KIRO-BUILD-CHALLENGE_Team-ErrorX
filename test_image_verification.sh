#!/bin/bash
BASE_URL="http://localhost:8000"

LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')
TOKEN=$(echo "$LOGIN" | jq -r '.access_token')

# Create simple PNG image
python3 << 'PYTHON'
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('/tmp/test_image.png')
print("Image created")
PYTHON

echo "Uploading PNG image..."
UPLOAD=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_image.png" \
  -F "title=Test Image PNG" \
  -F "description=Testing image verification")

DOC_ID=$(echo "$UPLOAD" | jq -r '.id')
echo "Document ID: $DOC_ID"

echo -e "\nVerifying image..."
VERIFY=$(curl -s -X POST "$BASE_URL/documents/$DOC_ID/verify" \
  -H "Authorization: Bearer $TOKEN")

echo -e "\nStatus: $(echo "$VERIFY" | jq -r '.status')"
echo "Authenticity Score: $(echo "$VERIFY" | jq -r '.verification_result.authenticity_score')%"
echo "Fake Probability: $(echo "$VERIFY" | jq -r '.verification_result.fake_probability')%"
echo -e "\nImage Metadata:"
echo "$VERIFY" | jq '.verification_result.metadata'
