from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from app.models.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentStatus,
    VerificationResult, DetectionResult, DocumentVerificationResult
)
from app.routers.auth import get_current_user
from app.database.connection import get_database
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import hashlib
import os
import shutil
from PIL import Image
import mimetypes
import numpy as np
from app.analysis.document import ocr, verification

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

def detect_ai_generation_signals(img: Image.Image) -> tuple[bool, float, str, list]:
    """
    Detect AI-generation indicators using statistical image analysis.
    Returns: (detected, confidence, details, risk_list)
    """
    ai_indicators = []
    ai_confidence = 0.0
    
    try:
        # Convert to numpy for analysis
        img_array = np.array(img.convert('RGB'))
        height, width = img_array.shape[:2]
        
        # 1. Check for unnatural color distribution
        # AI images often have smoother color transitions
        color_variance = np.var(img_array, axis=(0, 1)).mean()
        if color_variance < 500:  # Very smooth
            ai_indicators.append("Unusually smooth color distribution")
            ai_confidence += 15.0
        
        # 2. Check for texture repetition patterns
        # AI generators sometimes create repetitive patterns
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        
        # Sample regions and compare
        if height > 100 and width > 100:
            region1 = gray[10:50, 10:50]
            region2 = gray[height-50:height-10, width-50:width-10]
            correlation = np.corrcoef(region1.flatten(), region2.flatten())[0, 1]
            
            if correlation > 0.85:  # High similarity in distant regions
                ai_indicators.append("Repetitive texture patterns detected")
                ai_confidence += 20.0
        
        # 3. Check for synthetic metadata indicators
        # AI tools often lack proper camera EXIF or have suspicious software tags
        exif = img.getexif()
        if exif:
            software_tag = exif.get(305, "")  # Software tag
            if any(keyword in str(software_tag).lower() for keyword in 
                   ['stable', 'diffusion', 'midjourney', 'dall', 'generate', 'ai', 'synthetic']):
                ai_indicators.append(f"AI generation software detected: {software_tag}")
                ai_confidence += 40.0
        
        # 4. Check aspect ratio - AI often uses specific ratios
        aspect_ratio = width / height if height > 0 else 1.0
        common_ai_ratios = [1.0, 1.5, 0.666, 2.0, 0.5]  # Square, 3:2, 2:3, 2:1, 1:2
        if any(abs(aspect_ratio - ratio) < 0.05 for ratio in common_ai_ratios):
            if width % 64 == 0 and height % 64 == 0:  # Divisible by 64 (common in AI models)
                ai_indicators.append(f"Dimensions ({width}x{height}) match AI model output")
                ai_confidence += 15.0
        
        # 5. Check for noise characteristics
        # Natural photos have more noise, AI images are often too clean
        noise_level = np.std(img_array)
        if noise_level < 20:  # Very low noise
            ai_indicators.append("Unnaturally low noise level")
            ai_confidence += 10.0
        
        # Cap confidence
        ai_confidence = min(ai_confidence, 95.0)
        
        detected = ai_confidence > 30.0  # Threshold for positive detection
        
        if detected:
            details = f"AI generation indicators detected (confidence: {ai_confidence:.1f}%): " + "; ".join(ai_indicators)
        elif ai_confidence > 10.0:
            details = f"Weak AI generation signals detected ({ai_confidence:.1f}%): " + "; ".join(ai_indicators)
        else:
            details = "No significant AI generation indicators detected"
        
        return detected, ai_confidence, details, ai_indicators
        
    except Exception as e:
        return False, 0.0, f"AI detection analysis failed: {str(e)}", []

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
    ai_generation_detected = False
    ai_confidence = 0.0
    
    if is_image:
        try:
            with Image.open(file_path) as img:
                metadata["image_format"] = img.format
                metadata["image_size"] = f"{img.width}x{img.height}"
                metadata["image_mode"] = img.mode
                
                # AI generation detection (statistical analysis)
                ai_detected, ai_conf, ai_details, ai_indicators = detect_ai_generation_signals(img)
                ai_generation_detected = ai_detected
                ai_confidence = ai_conf
                
                if ai_generation_detected:
                    risk_factors.append("AI generation indicators detected")
                    for indicator in ai_indicators:
                        risk_factors.append(indicator)
                    
                    detections.append(DetectionResult(
                        name="AI Content Detection",
                        detected=True,
                        confidence=ai_confidence,
                        details=ai_details,
                        severity="high" if ai_confidence > 60 else "warning"
                    ))
                elif ai_conf > 10.0:
                    detections.append(DetectionResult(
                        name="AI Content Detection",
                        detected=False,
                        confidence=ai_confidence,
                        details=ai_details,
                        severity="warning"
                    ))
                else:
                    detections.append(DetectionResult(
                        name="AI Content Detection",
                        detected=False,
                        confidence=ai_confidence,
                        details=ai_details,
                        severity=None
                    ))
                
                # EXIF metadata check
                exif_data = img.getexif()
                has_exif = exif_data is not None and len(exif_data) > 0
                
                if has_exif:
                    exif_details = f"EXIF data found ({len(exif_data)} fields)"
                    
                    # Extract useful EXIF info
                    if 271 in exif_data:  # Make
                        metadata["camera_make"] = str(exif_data[271])
                    if 272 in exif_data:  # Model
                        metadata["camera_model"] = str(exif_data[272])
                    if 306 in exif_data:  # DateTime
                        metadata["date_taken"] = str(exif_data[306])
                    
                    # Check if EXIF looks synthetic
                    software = exif_data.get(305, "")
                    if any(kw in str(software).lower() for kw in ['stable', 'diffusion', 'midjourney', 'dall', 'ai']):
                        risk_factors.append("AI generation software detected in EXIF")
                        exif_details += " - AI generation software detected"
                    elif metadata.get("camera_make") and metadata.get("camera_model"):
                        confidence_factors.append("Camera metadata present")
                        exif_details += " - Camera information verified"
                    # Note: EXIF without camera data is neutral, not suspicious
                else:
                    # Missing EXIF is NORMAL for many legitimate images
                    exif_details = "No EXIF metadata - common for screenshots, social media images, or edited photos"
                
                detections.append(DetectionResult(
                    name="Metadata Analysis",
                    detected=has_exif,
                    confidence=None,
                    details=exif_details,
                    severity=None  # Not a warning - missing EXIF is normal
                ))
                
                # File format analysis
                format_analysis = f"Image format: {img.format}"
                if img.format in ['PNG', 'WEBP']:
                    format_analysis += " - common for screenshots and web images"
                    # PNG/WEBP alone is NOT a risk factor - very common for legitimate images
                elif img.format == 'JPEG':
                    format_analysis += " - standard photo format"
                    if not ai_generation_detected and has_exif and metadata.get("camera_make"):
                        confidence_factors.append("Camera photo with metadata")
                
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
            # Also add AI detection failure
            detections.append(DetectionResult(
                name="AI Content Detection",
                detected=False,
                confidence=None,
                details=f"Analysis failed: {str(e)}",
                severity=None
            ))
    else:
        # Non-image files
        detections.append(DetectionResult(
            name="AI Content Detection",
            detected=False,
            confidence=None,
            details="Not applicable for non-image files",
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
    elif ai_generation_detected and ai_confidence > 60:
        # Strong AI generation signal
        overall_status = DocumentStatus.SUSPICIOUS
        status_reason = f"AI generation detected (confidence: {ai_confidence:.1f}%)"
    elif ai_generation_detected and ai_confidence > 40:
        # Moderate AI signal
        overall_status = DocumentStatus.MANUAL_REVIEW
        status_reason = f"Possible AI generation (confidence: {ai_confidence:.1f}%) - manual review recommended"
    elif len(risk_factors) >= 3:
        # Multiple risk factors
        overall_status = DocumentStatus.SUSPICIOUS
        status_reason = f"Multiple risk indicators: {', '.join(risk_factors[:3])}"
    elif len(confidence_factors) >= 1 and not ai_generation_detected:
        # Has positive signals and no AI detected
        overall_status = DocumentStatus.VERIFIED
        status_reason = f"Passed available checks: {', '.join(confidence_factors)}"
    elif len(risk_factors) == 0 and not ai_generation_detected:
        # No risk factors, no AI detected - normal image
        overall_status = DocumentStatus.VERIFIED
        status_reason = "No suspicious indicators detected in available checks"
    else:
        # Insufficient data
        overall_status = DocumentStatus.MANUAL_REVIEW
        status_reason = "Insufficient data for automated classification"
    
    metadata["status_reason"] = status_reason
    metadata["risk_factors"] = risk_factors
    metadata["confidence_factors"] = confidence_factors
    
    # Calculate confidence scores based on real signals
    authenticity_score = None
    fake_probability = None
    
    if not hash_match:
        authenticity_score = 0.0
        fake_probability = 100.0
    elif ai_generation_detected:
        # AI detected - use AI confidence
        fake_probability = ai_confidence
        authenticity_score = 100.0 - fake_probability
    elif overall_status == DocumentStatus.VERIFIED:
        # Verified - high authenticity
        base_score = 75.0
        if len(confidence_factors) >= 2:
            base_score = 90.0
        authenticity_score = min(base_score, 95.0)
        fake_probability = 100.0 - authenticity_score
    elif overall_status == DocumentStatus.SUSPICIOUS:
        # Suspicious - calculate based on risk factors
        fake_probability = min(float(len(risk_factors) * 20 + 40), 85.0)
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
    document_type: str = Form(None),  # For document verification
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
        "document_type": document_type,
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


@router.post("/{document_id}/verify-document", response_model=DocumentResponse)
async def verify_id_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Verify ID document (Aadhaar, PAN, etc.) with OCR and authenticity checks"""
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
    
    file_path = document["file_path"]
    selected_doc_type = document.get("document_type", "general")
    
    try:
        # Step 1: OCR - Extract text
        extracted_text = ocr.extract_text(file_path)
        
        # Step 2: Detect document type
        detected_type = ocr.detect_document_type(extracted_text)
        type_match = detected_type == selected_doc_type if detected_type else False
        
        # Step 3: Extract fields based on document type
        extracted_fields = {}
        if detected_type:
            extracted_fields = ocr.extract_document_fields(detected_type, extracted_text)
        elif selected_doc_type != "general":
            extracted_fields = ocr.extract_document_fields(selected_doc_type, extracted_text)
        
        # Step 4: Structure check
        structure_ok, structure_conf, structure_details = verification.check_document_structure(
            file_path, selected_doc_type
        )
        structure_check = DetectionResult(
            name="Document Structure",
            detected=structure_ok,
            confidence=structure_conf,
            details=structure_details,
            severity="warning" if not structure_ok else None
        )
        
        # Step 5: Manipulation check
        manip_detected, manip_conf, manip_details, manip_findings = verification.check_image_manipulation(file_path)
        manipulation_check = DetectionResult(
            name="Image Manipulation",
            detected=manip_detected,
            confidence=manip_conf,
            details=manip_details,
            severity="high" if manip_detected else None
        )
        
        # Step 6: Text consistency
        text_consistent, text_details = verification.check_text_consistency(extracted_text, extracted_fields)
        text_consistency_check = DetectionResult(
            name="Text Consistency",
            detected=text_consistent,
            confidence=None,
            details=text_details,
            severity="warning" if not text_consistent else None
        )
        
        # Step 7: Field validations
        field_validations = []
        for field_name, field_value in extracted_fields.items():
            is_valid, validation_msg = verification.validate_field_format(
                field_name, field_value, selected_doc_type
            )
            field_validations.append(DetectionResult(
                name=f"{field_name.replace('_', ' ').title()} Format",
                detected=is_valid,
                confidence=None,
                details=validation_msg,
                severity="warning" if not is_valid else None
            ))
        
        # Calculate overall status
        risk_count = sum([
            not structure_ok,
            manip_detected,
            not text_consistent,
            not type_match if detected_type else False
        ])
        
        if risk_count >= 2:
            overall_status = DocumentStatus.SUSPICIOUS
            confidence_score = 30.0
        elif risk_count == 1:
            overall_status = DocumentStatus.MANUAL_REVIEW
            confidence_score = 60.0
        elif structure_ok and text_consistent:
            overall_status = DocumentStatus.VERIFIED
            confidence_score = 85.0
        else:
            overall_status = DocumentStatus.MANUAL_REVIEW
            confidence_score = 50.0
        
        # Limitations
        limitations = [
            "Official issuer verification not available",
            "OCR accuracy depends on image quality",
            "Visual checks only - cannot verify against government database"
        ]
        
        # Build result
        doc_verification_result = DocumentVerificationResult(
            document_type_detected=detected_type,
            document_type_match=type_match,
            extracted_text=extracted_text[:500] if extracted_text else "",  # Truncate for storage
            extracted_fields=extracted_fields,
            structure_check=structure_check,
            manipulation_check=manipulation_check,
            text_consistency=text_consistency_check,
            field_validations=field_validations,
            overall_status=overall_status,
            confidence_score=confidence_score,
            limitations=limitations,
            analyzed_at=datetime.utcnow()
        )
        
        # Update document
        db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {
                "status": overall_status,
                "document_verification_result": doc_verification_result.model_dump(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Get updated document
        updated_document = db.documents.find_one({"_id": ObjectId(document_id)})
        updated_document["id"] = str(updated_document["_id"])
        
        return DocumentResponse(**updated_document)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document verification failed: {str(e)}"
        )
