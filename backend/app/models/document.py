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
    created_at: datetime
    updated_at: datetime
    verification_result: Optional[VerificationResult] = None
    
    class Config:
        from_attributes = True
