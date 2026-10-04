import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from typing import Dict, List, Optional, Tuple

def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess image for better OCR accuracy"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def extract_text(image_path: str) -> str:
    """Extract text from image using OCR"""
    try:
        preprocessed = preprocess_image(image_path)
        text = pytesseract.image_to_string(preprocessed, lang='eng')
        return text.strip()
    except Exception as e:
        # Fallback to direct OCR without preprocessing
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='eng')
            return text.strip()
        except:
            return ""

def detect_document_type(text: str) -> Optional[str]:
    """Detect document type from extracted text"""
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['aadhaar', 'aadhar', 'uidai', 'unique identification']):
        return 'aadhaar'
    elif any(keyword in text_lower for keyword in ['permanent account number', 'income tax', 'pan card']):
        return 'pan'
    elif any(keyword in text_lower for keyword in ['ration card', 'राशन कार्ड', 'food security']):
        return 'ration_card'
    elif any(keyword in text_lower for keyword in ['driving licence', 'driving license', 'transport authority']):
        return 'driving_licence'
    elif any(keyword in text_lower for keyword in ['death certificate', 'certificate of death', 'deceased']):
        return 'death_certificate'
    
    return None

def extract_aadhaar_info(text: str) -> Dict[str, Optional[str]]:
    """Extract Aadhaar card information"""
    info = {}
    lines = text.split('\n')
    
    # Extract Aadhaar number (12 digits)
    aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    match = re.search(aadhaar_pattern, text)
    info['aadhaar_number'] = match.group(0).replace(' ', '') if match else None
    
    # Extract DOB
    dob_patterns = [
        r'DOB[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
        r'Date of Birth[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
        r'Year of Birth[:\s]+(\d{4})'
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['dob'] = match.group(1)
            break
    
    # Extract Gender
    if re.search(r'\b(Male|Female|MALE|FEMALE)\b', text):
        match = re.search(r'\b(Male|Female|MALE|FEMALE)\b', text)
        info['gender'] = match.group(1).title() if match else None
    
    # Extract name (heuristic: usually first non-empty line after header)
    potential_names = [line.strip() for line in lines if len(line.strip()) > 3 and not any(
        keyword in line.lower() for keyword in ['government', 'aadhaar', 'india', 'dob', 'male', 'female']
    )]
    info['name'] = potential_names[0] if potential_names else None
    
    return info

def extract_pan_info(text: str) -> Dict[str, Optional[str]]:
    """Extract PAN card information"""
    info = {}
    
    # Extract PAN number (format: XXXXX9999X)
    pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
    match = re.search(pan_pattern, text)
    info['pan_number'] = match.group(0) if match else None
    
    # Extract DOB
    dob_pattern = r'(\d{2}[/-]\d{2}[/-]\d{4})'
    match = re.search(dob_pattern, text)
    info['dob'] = match.group(1) if match else None
    
    # Extract name
    lines = text.split('\n')
    potential_names = [line.strip() for line in lines if len(line.strip()) > 3 and not any(
        keyword in line.lower() for keyword in ['income', 'tax', 'permanent', 'account', 'signature']
    )]
    info['name'] = potential_names[0] if potential_names else None
    
    return info

def extract_dl_info(text: str) -> Dict[str, Optional[str]]:
    """Extract Driving Licence information"""
    info = {}
    
    # Extract DL number
    dl_patterns = [
        r'\b[A-Z]{2}[-\s]?\d{2,4}[-\s]?\d{4}[-\s]?\d{7}\b',
        r'\b[A-Z]{2}\d{13}\b'
    ]
    for pattern in dl_patterns:
        match = re.search(pattern, text)
        if match:
            info['dl_number'] = match.group(0)
            break
    
    # Extract DOB
    dob_pattern = r'DOB[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})'
    match = re.search(dob_pattern, text, re.IGNORECASE)
    info['dob'] = match.group(1) if match else None
    
    # Extract validity dates
    validity_pattern = r'Valid Till[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})'
    match = re.search(validity_pattern, text, re.IGNORECASE)
    info['valid_till'] = match.group(1) if match else None
    
    return info

def extract_ration_card_info(text: str) -> Dict[str, Optional[str]]:
    """Extract Ration Card information"""
    info = {}
    
    # Extract card number
    card_pattern = r'\b\d{10,15}\b'
    match = re.search(card_pattern, text)
    info['card_number'] = match.group(0) if match else None
    
    return info

def extract_death_certificate_info(text: str) -> Dict[str, Optional[str]]:
    """Extract Death Certificate information"""
    info = {}
    
    # Extract registration number
    reg_pattern = r'Registration No[.:\s]+([A-Z0-9/-]+)'
    match = re.search(reg_pattern, text, re.IGNORECASE)
    info['registration_number'] = match.group(1) if match else None
    
    # Extract date of death
    death_date_patterns = [
        r'Date of Death[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
        r'Died on[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})'
    ]
    for pattern in death_date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['date_of_death'] = match.group(1)
            break
    
    return info

def extract_document_fields(doc_type: str, text: str) -> Dict[str, Optional[str]]:
    """Extract fields based on document type"""
    extractors = {
        'aadhaar': extract_aadhaar_info,
        'pan': extract_pan_info,
        'driving_licence': extract_dl_info,
        'ration_card': extract_ration_card_info,
        'death_certificate': extract_death_certificate_info
    }
    
    extractor = extractors.get(doc_type)
    if extractor:
        return extractor(text)
    return {}
