from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from app.models.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentStatus
from app.routers.auth import get_current_user
from app.database.connection import get_database
from datetime import datetime
from bson import ObjectId
from typing import List
import hashlib
import os
import shutil

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
    """Verify document authenticity by checking file hash"""
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
    
    # Recalculate file hash
    if not os.path.exists(document["file_path"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    current_hash = calculate_file_hash(document["file_path"])
    
    # Compare hashes
    new_status = DocumentStatus.VERIFIED if current_hash == document["file_hash"] else DocumentStatus.REJECTED
    
    db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )
    
    # Get updated document
    updated_document = db.documents.find_one({"_id": ObjectId(document_id)})
    updated_document["id"] = str(updated_document["_id"])
    
    return DocumentResponse(**updated_document)
