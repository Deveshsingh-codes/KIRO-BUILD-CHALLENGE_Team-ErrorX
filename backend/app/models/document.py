from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

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
    
    class Config:
        from_attributes = True
