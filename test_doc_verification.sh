#!/bin/bash
BASE_URL="http://localhost:8000"

LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')
TOKEN=$(echo "$LOGIN" | jq -r '.access_token')

# Create simulated document with text
python3 << 'PY'
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGB', (600, 400), color='white')
draw = ImageDraw.Draw(img)

# Simulate Aadhaar-like text
text = """
GOVERNMENT OF INDIA
UNIQUE IDENTIFICATION AUTHORITY

Name: RAJESH KUMAR
DOB: 15/08/1985
Male
Address: 123 MG Road, Bangalore
Aadhaar: 1234 5678 9012
"""

draw.text((50, 50), text.strip(), fill='black')
img.save('/tmp/test_aadhaar.jpg', 'JPEG')
print("Test document created")
PY

echo "Uploading test Aadhaar document..."
UPLOAD=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_aadhaar.jpg" \
  -F "title=Test Aadhaar" \
  -F "document_type=aadhaar")
DOC_ID=$(echo "$UPLOAD" | jq -r '.id')
echo "Document ID: $DOC_ID"

echo -e "\nVerifying document..."
VERIFY=$(curl -s -X POST "$BASE_URL/documents/$DOC_ID/verify-document" \
  -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY" | jq -r '.status')"
echo "Detected Type: $(echo "$VERIFY" | jq -r '.document_verification_result.document_type_detected')"
echo "Type Match: $(echo "$VERIFY" | jq -r '.document_verification_result.document_type_match')"
echo -e "\nExtracted Fields:"
echo "$VERIFY" | jq '.document_verification_result.extracted_fields'
echo -e "\nChecks:"
echo "Structure: $(echo "$VERIFY" | jq -r '.document_verification_result.structure_check.details')"
echo "Manipulation: $(echo "$VERIFY" | jq -r '.document_verification_result.manipulation_check.details')"
