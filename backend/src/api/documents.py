from fastapi import APIRouter, Depends, HTTPException, status, Cookie, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated

from src.db.database import get_db
from src.core.auth_middleware import RequireAdminOrOwnership, RequireAdminOrUser, RequireAuth
from src.core.config import settings
from src.services.document_service import DocumentService
from src.services.storage_service import upload_file_to_s3
from src.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentUploadResponse
from src.utils.cache import Cache
from src.models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse, responses={
    200: {"description": "File uploaded successfully"}, 
    400: {"description": "Invalid file or upload error"},
    401: {"description": "Authentication required"},
    413: {"description": "File too large"},
    500: {"description": "Server error during upload"}
})
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(RequireAdminOrUser)
):
    """
    Upload a document file to S3 storage and return the file URL.
    
    This endpoint accepts a file upload and stores it in S3, returning the public URL.
    The file will be given a unique name to prevent conflicts.
    
    Supported file types: PDF, DOC, DOCX, TXT, JPG, JPEG, PNG, GIF, CSV, XLS, XLSX
    Maximum file size: 10MB
    """
    
    # Check file size
    MAX_FILE_SIZE = settings.MAX_FILE_SIZE
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB."
        )
    
    # Check file type
    allowed_extensions = {
        'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'csv', 'xls', 'xlsx'
    }
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Supported types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Upload file to S3
        file_url = upload_file_to_s3(file.file, file.filename)
        
        return DocumentUploadResponse(
            file_url=file_url,
            filename=file.filename,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from storage service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during file upload: {str(e)}"
        )

@router.post("/", response_model=DocumentResponse, responses={201: {"description": "Document created successfully."}, 400: {"description": "Invalid input."}})
def create_document(
    document: DocumentCreate, 
    db: Session = Depends(get_db), 
    session_token: Annotated[Optional[str], Cookie()] = None
):
    """Create a new document record."""
    RequireAdminOrUser(user_id=document.user_id,session_token=session_token, db=db)
    
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
def update_document(document_id: int, document_update: DocumentUpdate, db: Session = Depends(get_db), isAuthenticated: bool = Depends(RequireAdminOrOwnership)):
    """Update an existing document record."""
    document = DocumentService.update_document(db, document_id, document_update)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    Cache.delete(f"documents_user_{document.user_id}")
    return document

@router.delete("/{document_id}", responses={200: {"description": "Document deleted successfully."}, 404: {"description": "Document not found."}})
def delete_document(document_id: int, db: Session = Depends(get_db), isAuthenticated: bool = Depends(RequireAdminOrOwnership)):
    """Delete a document by its ID."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    Cache.delete(f"documents_user_{document.user_id}")
    return {"message": "Document deleted successfully"}
