from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPICIOUS = "suspicious"
    MANUAL_REVIEW = "manual_review"

class DocumentType(str, Enum):
    GENERAL = "general"
    AADHAAR = "aadhaar"
    PAN = "pan"
    RATION_CARD = "ration_card"
    DRIVING_LICENCE = "driving_licence"
    DEATH_CERTIFICATE = "death_certificate"

class DetectionResult(BaseModel):
    name: str
    detected: bool
    confidence: Optional[float] = None
    details: Optional[str] = None
    severity: Optional[str] = None

class VerificationResult(BaseModel):
    overall_status: DocumentStatus
    authenticity_score: Optional[float] = None  # 0-100, higher = more authentic
    fake_probability: Optional[float] = None  # 0-100, higher = more likely fake
    detections: List[DetectionResult] = []
    metadata: Dict[str, Any] = {}
    analyzed_at: datetime

class DocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    file_hash: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    file_path: str
    file_hash: str
    status: DocumentStatus
    document_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    verification_result: Optional[VerificationResult] = None
    document_verification_result: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class DocumentVerificationResult(BaseModel):
    document_type_detected: Optional[str] = None
    document_type_match: bool = False
    extracted_text: str = ""
    extracted_fields: Dict[str, Any] = {}
    structure_check: DetectionResult
    manipulation_check: DetectionResult
    text_consistency: DetectionResult
    field_validations: List[DetectionResult] = []
    overall_status: DocumentStatus
    confidence_score: Optional[float] = None
    limitations: List[str] = []
    analyzed_at: datetime
