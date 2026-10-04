# AI Detection Fix

## Why AI Images Were Classified as REAL

**Root Cause (Lines 163-165 in old code):**
```python
elif len(confidence_factors) >= 2:
    overall_status = DocumentStatus.VERIFIED
```

**The Problem:**
1. AI-generated JPEG with synthetic EXIF → 2 confidence factors → **VERIFIED**
2. No actual AI detection was performed
3. Logic only checked: hash integrity + EXIF presence + format
4. AI tools can add fake EXIF with camera make/model
5. Result: AI images with fake camera metadata passed as REAL

## Detection Logic Added

### Statistical AI Generation Detection
Added `detect_ai_generation_signals()` function using:

**1. Color Distribution Analysis**
- Natural photos: varied color variance
- AI images: unusually smooth (variance < 500)
- Signal: +15% confidence if detected

**2. Texture Repetition Detection**
- Samples distant image regions
- Calculates correlation coefficient
- AI generators create repetitive patterns
- Signal: +20% confidence if correlation > 0.85

**3. Synthetic Metadata Detection**
- Scans EXIF software tag
- Detects: "stable diffusion", "midjourney", "dall-e", "ai", "synthetic"
- Signal: +40% confidence if found

**4. Dimension Analysis**
- AI models output specific ratios (1:1, 3:2, 2:1)
- Dimensions divisible by 64 (model architecture)
- Signal: +15% confidence if matched

**5. Noise Level Analysis**
- Natural photos: higher noise (std > 20)
- AI images: unnaturally clean (std < 20)
- Signal: +10% confidence if too clean

**Detection Threshold:** >30% confidence = positive detection

### Classification Logic (Fixed)
```python
if ai_generation_detected and ai_confidence > 60:
    status = SUSPICIOUS (overrides other factors)
elif risk_factors >= 3:
    status = SUSPICIOUS
elif risk_factors >= 2:
    status = SUSPICIOUS
elif confidence_factors >= 2 AND NOT ai_detected:
    status = VERIFIED
else:
    status = MANUAL_REVIEW
```

**Key Fix:** VERIFIED requires NO AI detection + positive signals

## Real Signals Used

### Currently Active:
1. ✅ **File Integrity** - SHA256 hash check
2. ✅ **AI Content Detection** - Statistical image analysis (NEW)
3. ✅ **Metadata Analysis** - EXIF presence, camera data, software tags
4. ✅ **Format Analysis** - JPEG/PNG patterns
5. ✅ **Dimension Analysis** - AI model output patterns
6. ✅ **Noise Analysis** - Synthetic smoothness detection
7. ✅ **Texture Analysis** - Repetition patterns

### Marked Unavailable:
- ⚠️ Deepfake Detection (requires ML model)
- ⚠️ Source Verification (requires database)

## Test Results

```
Camera Photo (Canon EOS R5, realistic noise, 1920x1280):
  Status: VERIFIED
  Authenticity: 100% | AI Risk: 0%
  AI Detection: false (15% weak signals)
  Reason: File integrity verified, Camera metadata present, Standard photo format

AI-Generated (512x512, smooth, low noise):
  Status: SUSPICIOUS  
  Authenticity: 50% | AI Risk: 50%
  AI Detection: true (50% confidence)
  Signals: Smooth color distribution, Repetitive textures, Dimensions match AI output
  Reason: AI generation indicators detected

Stable Diffusion (explicit software tag):
  Status: SUSPICIOUS
  Authenticity: 20% | AI Risk: 80%
  AI Detection: true (80% confidence)
  Signals: AI software detected in EXIF
  Reason: AI generation detected (80% confidence)

Screenshot (no EXIF, 1366x768):
  Status: SUSPICIOUS
  Authenticity: 30% | AI Risk: 70%
  AI Detection: false (25% weak signals)
  Reason: No camera metadata, Format used for generated content
```

## Genuine Limitations

1. **Statistical Analysis Only** - Not a trained ML classifier
2. **Can Be Fooled** - Sophisticated AI with added noise/EXIF may evade
3. **False Positives Possible** - Heavily edited real photos may trigger
4. **No Frame-by-Frame** - Video analysis not implemented
5. **No Semantic Analysis** - Doesn't understand image content (faces, objects)

**For Production:** Integrate trained ML model (e.g., CLIP-based detector, CNN classifier)

## Architecture

Detection is **extensible**:
- Add ML model → Update `detect_ai_generation_signals()`
- Append new `DetectionResult` to list
- Frontend displays automatically
- No UI changes needed

## Scoring Transparency

Scores now based on:
- AI detection confidence directly used as fake probability
- Risk factors count (each adds ~20%)
- Confidence factors count (each adds ~25%)
- Returns `null` when inconclusive (not fake 95%)

No hardcoded defaults remain.
