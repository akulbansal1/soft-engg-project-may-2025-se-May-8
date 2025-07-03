from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.document import Document
from src.schemas.document import DocumentCreate, DocumentUpdate

class DocumentService:
    """Service class for Document CRUD operations."""

    @staticmethod
    def create_document(db: Session, document_in: DocumentCreate) -> Document:
        """Create a new document record."""
        document = Document(**document_in.model_dump())
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[Document]:
        """Get a document by its ID."""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_documents_by_user(db: Session, user_id: int) -> List[Document]:
        """Get all documents for a user."""
        return db.query(Document).filter(Document.user_id == user_id).all()

    @staticmethod
    def update_document(db: Session, document_id: int, document_in: DocumentUpdate) -> Optional[Document]:
        """Update a document record."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        for field, value in document_in.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """Delete a document record."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        db.delete(document)
        db.commit()
        return True
