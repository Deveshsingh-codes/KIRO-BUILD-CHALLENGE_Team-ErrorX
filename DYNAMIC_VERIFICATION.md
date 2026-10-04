# Dynamic Verification Fix

## Root Cause
Lines 68-72 in `backend/app/routers/documents.py` **hardcoded** `authenticity_score = 95.0` and `fake_probability = 5.0` for ALL files passing hash check.

## Files Changed (6)

**Backend:**
1. `backend/app/routers/documents.py` - Replaced hardcoded scores with signal-based calculation

**Frontend:**
2. `frontend/src/pages/Dashboard.tsx` - Added processing UI, evidence display, guide link
3. `frontend/src/pages/Dashboard.css` - Added processing animation, evidence styling
4. `frontend/src/pages/VerificationGuide.tsx` - Complete verification guidebook
5. `frontend/src/pages/VerificationGuide.css` - Guidebook styling
6. `frontend/src/App.tsx` - Added /guide route

## How Dynamic Results Work

### Signal Collection
Analysis collects **real signals**:
- ✓ File integrity (hash match)
- ✓ EXIF metadata presence
- ✓ Camera make/model/timestamp extraction
- ✓ File format (JPEG=camera, PNG/WEBP=synthetic indicator)
- ✓ Image structure analysis

### Scoring Algorithm
```python
confidence_factors = ["File integrity verified", "Original metadata present", "Standard photo format"]
risk_factors = ["No camera metadata", "Format often used for generated content"]

if hash_mismatch:
    authenticity = 0%, fake = 100%
elif len(confidence_factors) >= 2:
    status = VERIFIED
    authenticity = min(len(factors) * 25 + 25, 100%)
elif len(risk_factors) >= 2:
    status = SUSPICIOUS
    fake = min(len(risks) * 25 + 30, 95%)
else:
    status = MANUAL_REVIEW
    scores = null (inconclusive)
```

### Test Results
```
Image WITH EXIF (camera photo):
  Status: verified
  Authenticity: 100% | Fake Risk: 0%
  Reason: File integrity verified, Original metadata present, Standard photo format

Image WITHOUT EXIF (PNG):
  Status: suspicious
  Authenticity: 20% | Fake Risk: 80%
  Reason: No camera metadata, Format often used for generated content

Text File:
  Status: manual_review
  Authenticity: null | Fake Risk: null
  Reason: Insufficient data for automated classification
```

## Guidebook Added

Accessible at http://localhost:5174/guide

**Sections:**
1. What is Image Verification?
2. Metadata Analysis (EXIF explained)
3. File Structure & Integrity
4. Compression Analysis
5. Visual Manipulation Indicators
6. AI-Generated Image Indicators (+ critical note about ML requirement)
7. Source & Cross-Validation
8. Understanding Results (Verified/Suspicious/Manipulated/Inconclusive)
9. Best Practices for Users
10. Privacy & Security

**Key messaging:**
- "Missing metadata alone does NOT prove fake"
- "Visual inspection cannot reliably prove AI generation"
- "Results are analytical assessments, not guarantees"

## Processing Experience

When verifying, UI shows:
```
[Spinner animation]
↓
Analyzing file structure...
Extracting metadata...
Checking integrity...
Generating report...
```

Then displays:
- Overall status badge
- Scores (ONLY if calculated from signals)
- "Why this result?" evidence section
- ✓ Confidence factors list
- ⚠ Risk factors list
- Detection breakdown
- File metadata

## Verification Status

✅ **Different files produce different scores**
✅ **Scores based on real signals (not hardcoded)**
✅ **Inconclusive cases return null (not fake scores)**
✅ **Evidence explains why result occurred**
✅ **Processing animation shows real analysis**
✅ **Guidebook educates users**

## Limitations

1. **No AI/ML models** - Advanced detections marked "not available"
2. **Basic signals only** - EXIF, format, integrity checks
3. **No video frame analysis** - Would need video processing library
4. **No deepfake detection** - Requires trained ML model
5. **Scores are estimates** - Based on limited available signals

Architecture ready for ML integration - just add detection functions and append real DetectionResults.
