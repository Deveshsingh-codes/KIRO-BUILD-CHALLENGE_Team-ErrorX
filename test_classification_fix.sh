#!/bin/bash
BASE_URL="http://localhost:8000"

LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')
TOKEN=$(echo "$LOGIN" | jq -r '.access_token')

echo "=== TEST 1: Normal Screenshot (PNG, no EXIF) ==="
python3 << 'PY'
from PIL import Image
import numpy as np
img = Image.new('RGB', (1366, 768), color=(180, 200, 220))
arr = np.array(img)
noise = np.random.normal(0, 25, arr.shape).astype(np.uint8)
arr = np.clip(arr.astype(int) + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)
img.save('/tmp/normal_screenshot.png', 'PNG')
print("Created")
PY

UPLOAD1=$(curl -s -X POST "$BASE_URL/documents/upload" -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/normal_screenshot.png" -F "title=Screenshot")
ID1=$(echo "$UPLOAD1" | jq -r '.id')
VERIFY1=$(curl -s -X POST "$BASE_URL/documents/$ID1/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY1" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY1" | jq -r '.verification_result.authenticity_score')%"
echo "Reason: $(echo "$VERIFY1" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== TEST 2: Camera Photo (JPEG with EXIF) ==="
python3 << 'PY'
from PIL import Image
import numpy as np
np.random.seed(100)
arr = np.random.randint(80, 180, (1920, 1280, 3), dtype=np.uint8)
noise = np.random.normal(0, 30, arr.shape).astype(np.uint8)
arr = np.clip(arr.astype(int) + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)
exif = img.getexif()
exif[271] = "Sony"
exif[272] = "Alpha A7"
img.save('/tmp/camera_photo.jpg', 'JPEG', exif=exif)
print("Created")
PY

UPLOAD2=$(curl -s -X POST "$BASE_URL/documents/upload" -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/camera_photo.jpg" -F "title=Photo")
ID2=$(echo "$UPLOAD2" | jq -r '.id')
VERIFY2=$(curl -s -X POST "$BASE_URL/documents/$ID2/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY2" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY2" | jq -r '.verification_result.authenticity_score')%"
echo "Reason: $(echo "$VERIFY2" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== TEST 3: AI-Generated (512x512, smooth, low noise) ==="
python3 << 'PY'
from PIL import Image
import numpy as np
img = Image.new('RGB', (512, 512), color=(120, 150, 180))
arr = np.array(img)
for i in range(512):
    arr[i, :, 0] = np.clip(120 + i * 0.1, 0, 255)
img = Image.fromarray(arr.astype(np.uint8))
img.save('/tmp/ai_generated.png', 'PNG')
print("Created")
PY

UPLOAD3=$(curl -s -X POST "$BASE_URL/documents/upload" -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/ai_generated.png" -F "title=AI Art")
ID3=$(echo "$UPLOAD3" | jq -r '.id')
VERIFY3=$(curl -s -X POST "$BASE_URL/documents/$ID3/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY3" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY3" | jq -r '.verification_result.authenticity_score')%"
echo "Fake Risk: $(echo "$VERIFY3" | jq -r '.verification_result.fake_probability')%"
echo "AI Confidence: $(echo "$VERIFY3" | jq -r '.verification_result.detections[] | select(.name=="AI Content Detection") | .confidence')%"
echo "Reason: $(echo "$VERIFY3" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== RESULTS ==="
echo "Screenshot: Should be VERIFIED (normal image)"
echo "Camera Photo: Should be VERIFIED (has camera metadata)"
echo "AI-Generated: Should be SUSPICIOUS (detected AI signals)"
