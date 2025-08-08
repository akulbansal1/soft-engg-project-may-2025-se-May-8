from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    """Base schema for document details."""
    name: str = Field(..., example="Prescription.pdf", description="Name of the document")
    file_url: str = Field(..., example="https://example.com/file.pdf", description="URL to the uploaded document")

class DocumentCreate(DocumentBase):
    """Schema for creating a new document record."""
    user_id: int = Field(..., example=1, description="ID of the user who owns the document")

class DocumentUpdate(BaseModel):
    """Schema for updating a document record (partial update)."""
    name: Optional[str] = Field(None, example="UpdatedName.pdf", description="Updated document name (optional)")
    file_url: Optional[str] = Field(None, example="https://example.com/updated.pdf", description="Updated file URL (optional)")

class DocumentResponse(DocumentBase):
    """Schema for returning document data to the client."""
    id: int = Field(..., example=1, description="Unique document ID")
    user_id: int = Field(..., example=1, description="ID of the user who owns the document")
    timestamp: datetime = Field(..., example="2025-06-25T12:00:00+00:00", description="Upload timestamp (ISO 8601)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Prescription.pdf",
                "file_url": "https://example.com/file.pdf",
                "user_id": 1,
                "timestamp": "2025-06-25T12:00:00+00:00"
            }
        }

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    file_url: str = Field(..., example="https://example.com/file.pdf", description="URL of the uploaded file")
    filename: str = Field(..., example="document.pdf", description="Original filename")
    message: str = Field(default="File uploaded successfully", description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "file_url": "https://example.com/file.pdf",
                "filename": "document.pdf",
                "message": "File uploaded successfully"
            }
        }
