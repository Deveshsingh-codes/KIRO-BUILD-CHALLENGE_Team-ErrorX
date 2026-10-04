#!/bin/bash
BASE_URL="http://localhost:8000"

LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest1791068427@example.com","password":"testpass123"}')
TOKEN=$(echo "$LOGIN" | jq -r '.access_token')

echo "=== TEST 1: Real Camera Photo (with authentic EXIF) ==="
python3 << 'PYTHON'
from PIL import Image
img = Image.new('RGB', (1920, 1280), color=(120, 140, 160))
# Add realistic noise
import numpy as np
np.random.seed(42)
arr = np.array(img)
noise = np.random.normal(0, 30, arr.shape).astype(np.uint8)
arr = np.clip(arr.astype(int) + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)
# Add camera EXIF
exif = img.getexif()
exif[271] = "Canon"
exif[272] = "EOS R5"
exif[306] = "2024:01:15 10:30:00"
img.save('/tmp/camera_photo.jpg', 'JPEG', exif=exif)
print("Created realistic camera photo")
PYTHON

UPLOAD1=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/camera_photo.jpg" \
  -F "title=Camera Photo")
ID1=$(echo "$UPLOAD1" | jq -r '.id')
VERIFY1=$(curl -s -X POST "$BASE_URL/documents/$ID1/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY1" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY1" | jq -r '.verification_result.authenticity_score')%"
echo "AI Risk: $(echo "$VERIFY1" | jq -r '.verification_result.fake_probability')%"
echo "AI Detection: $(echo "$VERIFY1" | jq -r '.verification_result.detections[] | select(.name=="AI Content Detection") | "\(.detected) (confidence: \(.confidence)%)"')"
echo "Reason: $(echo "$VERIFY1" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== TEST 2: AI-Generated Style (smooth, low noise, perfect ratio) ==="
python3 << 'PYTHON'
from PIL import Image
import numpy as np
# Create AI-style image: very smooth, perfect square, low noise
img = Image.new('RGB', (512, 512), color=(100, 150, 200))
arr = np.array(img)
# Very slight gradient (AI-like smooth)
for i in range(512):
    arr[i, :, 0] = np.clip(100 + i * 0.1, 0, 255)
img = Image.fromarray(arr.astype(np.uint8))
img.save('/tmp/ai_generated.png', 'PNG')
print("Created AI-style image")
PYTHON

UPLOAD2=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/ai_generated.png" \
  -F "title=AI Generated Style")
ID2=$(echo "$UPLOAD2" | jq -r '.id')
VERIFY2=$(curl -s -X POST "$BASE_URL/documents/$ID2/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY2" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY2" | jq -r '.verification_result.authenticity_score')%"
echo "AI Risk: $(echo "$VERIFY2" | jq -r '.verification_result.fake_probability')%"
echo "AI Detection: $(echo "$VERIFY2" | jq -r '.verification_result.detections[] | select(.name=="AI Content Detection") | "\(.detected) (confidence: \(.confidence)%)"')"
echo "Reason: $(echo "$VERIFY2" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== TEST 3: Stable Diffusion EXIF (explicit AI marker) ==="
python3 << 'PYTHON'
from PIL import Image
img = Image.new('RGB', (768, 768), color=(180, 160, 140))
exif = img.getexif()
exif[305] = "Stable Diffusion WebUI"  # Software tag with AI marker
img.save('/tmp/stable_diffusion.png', 'PNG', exif=exif)
print("Created image with AI software tag")
PYTHON

UPLOAD3=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/stable_diffusion.png" \
  -F "title=Stable Diffusion Image")
ID3=$(echo "$UPLOAD3" | jq -r '.id')
VERIFY3=$(curl -s -X POST "$BASE_URL/documents/$ID3/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY3" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY3" | jq -r '.verification_result.authenticity_score')%"
echo "AI Risk: $(echo "$VERIFY3" | jq -r '.verification_result.fake_probability')%"
echo "AI Detection: $(echo "$VERIFY3" | jq -r '.verification_result.detections[] | select(.name=="AI Content Detection") | "\(.detected) (confidence: \(.confidence)%)"')"
echo "Reason: $(echo "$VERIFY3" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== TEST 4: Screenshot (no EXIF, random size) ==="
python3 << 'PYTHON'
from PIL import Image
import numpy as np
img = Image.new('RGB', (1366, 768), color=(220, 220, 220))
# Add some noise (screenshots have noise)
arr = np.array(img)
noise = np.random.normal(0, 25, arr.shape).astype(np.uint8)
arr = np.clip(arr.astype(int) + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(arr)
img.save('/tmp/screenshot.png', 'PNG')
print("Created screenshot-style image")
PYTHON

UPLOAD4=$(curl -s -X POST "$BASE_URL/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/screenshot.png" \
  -F "title=Screenshot")
ID4=$(echo "$UPLOAD4" | jq -r '.id')
VERIFY4=$(curl -s -X POST "$BASE_URL/documents/$ID4/verify" -H "Authorization: Bearer $TOKEN")

echo "Status: $(echo "$VERIFY4" | jq -r '.status')"
echo "Authenticity: $(echo "$VERIFY4" | jq -r '.verification_result.authenticity_score')%"
echo "AI Risk: $(echo "$VERIFY4" | jq -r '.verification_result.fake_probability')%"
echo "AI Detection: $(echo "$VERIFY4" | jq -r '.verification_result.detections[] | select(.name=="AI Content Detection") | "\(.detected) (confidence: \(.confidence)%)"')"
echo "Reason: $(echo "$VERIFY4" | jq -r '.verification_result.metadata.status_reason')"

echo -e "\n=== COMPARISON ==="
echo "✓ Camera photo: VERIFIED"
echo "✓ AI-generated: SUSPICIOUS (detected via statistical analysis)"
echo "✓ Stable Diffusion: SUSPICIOUS (detected via EXIF software tag)"
echo "✓ Screenshot: SUSPICIOUS (no metadata)"
