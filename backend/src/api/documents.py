from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.document_service import DocumentService
from src.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/", response_model=DocumentResponse, responses={201: {"description": "Document created successfully."}, 400: {"description": "Invalid input."}})
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Create a new document record."""
    try:
        result = DocumentService.create_document(db, document)
        Cache.delete(f"documents_user_{document.user_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/{user_id}", response_model=List[DocumentResponse], responses={200: {"description": "List of documents for the user."}, 404: {"description": "User not found."}})
def get_documents_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all documents for a user."""
    cache_key = f"documents_user_{user_id}"
    cached_documents = Cache.get(cache_key)
    if cached_documents:
        return cached_documents
    documents = DocumentService.get_documents_by_user(db, user_id)
    documents_data = [DocumentResponse.model_validate(doc) for doc in documents]
    Cache.set(cache_key, [doc.model_dump() for doc in documents_data], expiry=300)
    return documents_data

@router.get("/{document_id}", response_model=DocumentResponse, responses={200: {"description": "Document found."}, 404: {"description": "Document not found."}})
def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """Get a document by its ID."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.put("/{document_id}", response_model=DocumentResponse, responses={200: {"description": "Document updated successfully."}, 404: {"description": "Document not found."}})
def update_document(document_id: int, document_update: DocumentUpdate, db: Session = Depends(get_db)):
    """Update an existing document record."""
    document = DocumentService.update_document(db, document_id, document_update)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    Cache.delete(f"documents_user_{document.user_id}")
    return document

@router.delete("/{document_id}", responses={200: {"description": "Document deleted successfully."}, 404: {"description": "Document not found."}})
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document by its ID."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    Cache.delete(f"documents_user_{document.user_id}")
    return {"message": "Document deleted successfully"}
