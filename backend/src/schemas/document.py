from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    name: str = Field(..., example="Prescription.pdf", description="Name of the document")
    file_url: str = Field(..., example="https://example.com/file.pdf", description="URL to the uploaded document")

class DocumentCreate(DocumentBase):
    user_id: int = Field(..., example=1, description="ID of the user who owns the document")

class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="UpdatedName.pdf")
    file_url: Optional[str] = Field(None, example="https://example.com/updated.pdf")

class DocumentResponse(DocumentBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    timestamp: datetime = Field(..., example="2025-06-25T12:00:00+00:00")

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    file_url: str = Field(..., example="https://example.com/file.pdf", description="URL of the uploaded file")
    filename: str = Field(..., example="document.pdf", description="Original filename")
    message: str = Field(default="File uploaded successfully", description="Success message")
