from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from app.models.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentStatus,
    VerificationResult, DetectionResult
)
from app.routers.auth import get_current_user
from app.database.connection import get_database
from datetime import datetime
from bson import ObjectId
from typing import List
import hashlib
import os
import shutil
from PIL import Image
import mimetypes
import numpy as np

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def analyze_file(file_path: str, file_hash: str) -> VerificationResult:
    """Perform file analysis based on available signals."""
    detections = []
    metadata = {}
    risk_factors = []
    confidence_factors = []
    
    # Get file info
    file_size = os.path.getsize(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    
    metadata["file_size"] = file_size
    metadata["mime_type"] = mime_type
    metadata["file_hash"] = file_hash
    
    # Hash integrity check
    current_hash = calculate_file_hash(file_path)
    hash_match = current_hash == file_hash
    
    if not hash_match:
        risk_factors.append("File modified after upload")
        detections.append(DetectionResult(
            name="File Integrity",
            detected=False,
            confidence=100.0,
            details="SHA256 hash does not match original - file has been modified",
            severity="critical"
        ))
    else:
        confidence_factors.append("File integrity verified")
        detections.append(DetectionResult(
            name="File Integrity",
            detected=True,
            confidence=100.0,
            details="SHA256 hash matches original",
            severity="low"
        ))
    
    # Image-specific analysis
    has_exif = False
    is_image = mime_type and mime_type.startswith('image/')
    
    if is_image:
        try:
            with Image.open(file_path) as img:
                metadata["image_format"] = img.format
                metadata["image_size"] = f"{img.width}x{img.height}"
                metadata["image_mode"] = img.mode
                
                # EXIF metadata check
                exif_data = img.getexif()
                has_exif = exif_data is not None and len(exif_data) > 0
                
                if has_exif:
                    confidence_factors.append("Original metadata present")
                    exif_details = f"EXIF data found ({len(exif_data)} fields)"
                    
                    # Extract useful EXIF info
                    if 271 in exif_data:  # Make
                        metadata["camera_make"] = str(exif_data[271])
                    if 272 in exif_data:  # Model
                        metadata["camera_model"] = str(exif_data[272])
                    if 306 in exif_data:  # DateTime
                        metadata["date_taken"] = str(exif_data[306])
                else:
                    risk_factors.append("No camera metadata")
                    exif_details = "EXIF data not found - may indicate screenshot, synthetic image, or metadata stripping"
                
                detections.append(DetectionResult(
                    name="Metadata Analysis",
                    detected=has_exif,
                    confidence=None,
                    details=exif_details,
                    severity="warning" if not has_exif else None
                ))
                
                # File format analysis
                format_analysis = f"Image format: {img.format}"
                if img.format in ['PNG', 'WEBP']:
                    format_analysis += " - commonly used for synthetic/edited images"
                    risk_factors.append("Format often used for generated content")
                elif img.format == 'JPEG':
                    format_analysis += " - typical camera output format"
                    confidence_factors.append("Standard photo format")
                
                detections.append(DetectionResult(
                    name="File Format Analysis",
                    detected=True,
                    confidence=None,
                    details=format_analysis,
                    severity=None
                ))
                
        except Exception as e:
            risk_factors.append("Image analysis failed")
            detections.append(DetectionResult(
                name="Image Structure",
                detected=False,
                confidence=None,
                details=f"Could not analyze image: {str(e)}",
                severity="warning"
            ))
    
    # Mark advanced AI detections as unavailable
    detections.append(DetectionResult(
        name="AI Content Detection",
        detected=False,
        confidence=None,
        details="ML-based AI detection not available - requires trained model integration",
        severity=None
    ))
    
    detections.append(DetectionResult(
        name="Deepfake Detection",
        detected=False,
        confidence=None,
        details="Face manipulation detection not available - requires ML model",
        severity=None
    ))
    
    detections.append(DetectionResult(
        name="Source Verification",
        detected=False,
        confidence=None,
        details="Cross-reference with trusted sources not available",
        severity=None
    ))
    
    # Calculate status based on real signals
    if not hash_match:
        overall_status = DocumentStatus.REJECTED
        status_reason = "File integrity check failed"
    elif len(risk_factors) >= 2:
        overall_status = DocumentStatus.SUSPICIOUS
        status_reason = f"Multiple risk indicators: {', '.join(risk_factors)}"
    elif len(confidence_factors) >= 2:
        overall_status = DocumentStatus.VERIFIED
        status_reason = f"Passed available checks: {', '.join(confidence_factors)}"
    else:
        overall_status = DocumentStatus.MANUAL_REVIEW
        status_reason = "Insufficient data for automated classification"
    
    metadata["status_reason"] = status_reason
    metadata["risk_factors"] = risk_factors
    metadata["confidence_factors"] = confidence_factors
    
    # Do NOT return fake scores - only return when meaningful
    authenticity_score = None
    fake_probability = None
    
    if not hash_match:
        # Clear manipulation detected
        authenticity_score = 0.0
        fake_probability = 100.0
    elif overall_status == DocumentStatus.VERIFIED and len(confidence_factors) >= 2:
        # Multiple positive signals - cap at 100
        authenticity_score = min(float(len(confidence_factors) * 25 + 25), 100.0)
        fake_probability = 100.0 - authenticity_score
    elif overall_status == DocumentStatus.SUSPICIOUS:
        # Risk factors present
        fake_probability = min(float(len(risk_factors) * 25 + 30), 95.0)
        authenticity_score = 100.0 - fake_probability
    # Otherwise leave as None (inconclusive)
    
    return VerificationResult(
        overall_status=overall_status,
        authenticity_score=authenticity_score,
        fake_probability=fake_probability,
        detections=detections,
        metadata=metadata,
        analyzed_at=datetime.utcnow()
    )

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Calculate file hash
    file_hash = calculate_file_hash(file_path)
    
    # Create document record
    document_dict = {
        "user_id": str(current_user["_id"]),
        "title": title or file.filename,
        "description": description,
        "file_path": file_path,
        "file_hash": file_hash,
        "status": DocumentStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.documents.insert_one(document_dict)
    document_dict["id"] = str(result.inserted_id)
    
    return DocumentResponse(**document_dict)

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    documents = list(db.documents.find({"user_id": str(current_user["_id"])}))
    
    for doc in documents:
        doc["id"] = str(doc["_id"])
    
    return [DocumentResponse(**doc) for doc in documents]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    try:
        document = db.documents.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document["id"] = str(document["_id"])
    return DocumentResponse(**document)

@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    try:
        document = db.documents.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update document
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": update_dict}
    )
    
    # Get updated document
    updated_document = db.documents.find_one({"_id": ObjectId(document_id)})
    updated_document["id"] = str(updated_document["_id"])
    
    return DocumentResponse(**updated_document)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    try:
        document = db.documents.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file
    try:
        if os.path.exists(document["file_path"]):
            os.remove(document["file_path"])
    except Exception as e:
        print(f"Failed to delete file: {str(e)}")
    
    # Delete document record
    db.documents.delete_one({"_id": ObjectId(document_id)})
    
    return None

@router.post("/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Verify document authenticity with detailed analysis"""
    db = get_database()
    
    try:
        document = db.documents.find_one({
            "_id": ObjectId(document_id),
            "user_id": str(current_user["_id"])
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not os.path.exists(document["file_path"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Perform analysis
    verification_result = analyze_file(document["file_path"], document["file_hash"])
    
    # Update document with results
    db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {
            "status": verification_result.overall_status,
            "verification_result": verification_result.model_dump(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Get updated document
    updated_document = db.documents.find_one({"_id": ObjectId(document_id)})
    updated_document["id"] = str(updated_document["_id"])
    
    return DocumentResponse(**updated_document)
