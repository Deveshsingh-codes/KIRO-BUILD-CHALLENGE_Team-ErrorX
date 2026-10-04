from PIL import Image
import numpy as np
from typing import Dict, List, Tuple
import cv2

def check_document_structure(image_path: str, doc_type: str) -> Tuple[bool, float, str]:
    """Check if document has expected structure"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, 0.0, "Could not read image"
        
        height, width = img.shape[:2]
        aspect_ratio = width / height if height > 0 else 0
        
        # Expected aspect ratios for documents (approximate)
        expected_ratios = {
            'aadhaar': (1.6, 1.7),  # ~85.6mm x 53.98mm
            'pan': (1.5, 1.6),
            'driving_licence': (1.5, 1.7),
            'ration_card': (1.4, 1.6),
            'death_certificate': (0.7, 1.5)  # More variable
        }
        
        if doc_type in expected_ratios:
            min_ratio, max_ratio = expected_ratios[doc_type]
            if min_ratio <= aspect_ratio <= max_ratio:
                return True, 85.0, f"Document aspect ratio ({aspect_ratio:.2f}) matches expected range"
            else:
                return False, 40.0, f"Aspect ratio ({aspect_ratio:.2f}) outside expected range ({min_ratio}-{max_ratio})"
        
        return True, 50.0, "Structure check completed (no specific template)"
    except Exception as e:
        return False, 0.0, f"Structure analysis failed: {str(e)}"

def check_image_manipulation(image_path: str) -> Tuple[bool, float, str, List[str]]:
    """Check for image manipulation indicators"""
    findings = []
    detected = False
    confidence = 0.0
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, 0.0, "Could not read image", []
        
        # Check for JPEG compression artifacts
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            if variance < 50:
                findings.append("Very low edge variance (possible heavy compression/editing)")
                confidence += 20
        
        # Check for inconsistent regions
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Check saturation consistency
        sat_std = np.std(s)
        if sat_std > 60:
            findings.append("Inconsistent color saturation across document")
            confidence += 15
        
        # Check for unusual noise patterns
        noise = np.std(img, axis=2).mean()
        if noise < 5:
            findings.append("Unnaturally uniform texture")
            confidence += 10
        elif noise > 40:
            findings.append("Excessive noise (possible scan quality issue)")
            confidence += 5
        
        detected = confidence > 25
        
        if detected:
            details = "Manipulation indicators detected: " + "; ".join(findings)
        elif findings:
            details = "Weak indicators: " + "; ".join(findings)
        else:
            details = "No significant manipulation indicators detected"
        
        return detected, min(confidence, 75.0), details, findings
        
    except Exception as e:
        return False, 0.0, f"Manipulation check failed: {str(e)}", []

def check_text_consistency(extracted_text: str, extracted_fields: Dict) -> Tuple[bool, str]:
    """Check if extracted text is internally consistent"""
    issues = []
    
    # Check if required fields were extracted
    if not extracted_text or len(extracted_text.strip()) < 10:
        issues.append("Insufficient text extracted")
    
    # Check field consistency
    missing_fields = [key for key, value in extracted_fields.items() if value is None]
    if len(missing_fields) > len(extracted_fields) / 2:
        issues.append(f"Many expected fields not detected: {', '.join(missing_fields)}")
    
    if issues:
        return False, "Consistency issues: " + "; ".join(issues)
    else:
        return True, "Extracted text appears internally consistent"

def validate_field_format(field_name: str, field_value: Optional[str], doc_type: str) -> Tuple[bool, str]:
    """Validate field format"""
    if field_value is None:
        return False, "Field not detected"
    
    import re
    
    # Aadhaar number: 12 digits
    if field_name == 'aadhaar_number':
        if re.match(r'^\d{12}$', field_value.replace(' ', '')):
            return True, "Valid format"
        return False, "Invalid Aadhaar format"
    
    # PAN number: XXXXX9999X
    if field_name == 'pan_number':
        if re.match(r'^[A-Z]{5}\d{4}[A-Z]$', field_value):
            return True, "Valid format"
        return False, "Invalid PAN format"
    
    # Date formats
    if 'dob' in field_name or 'date' in field_name:
        if re.match(r'\d{2}[/-]\d{2}[/-]\d{4}', field_value):
            return True, "Valid date format"
        if re.match(r'\d{4}', field_value):
            return True, "Year detected"
        return False, "Invalid date format"
    
    return True, "Format not strictly validated"
