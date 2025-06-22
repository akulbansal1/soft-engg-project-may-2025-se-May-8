from sqlalchemy.orm import Session
from src.models.emergency_contact import EmergencyContact
from src.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from typing import List, Optional

class EmergencyContactService:
    """
    Service for EmergencyContact CRUD operations
    """

    @staticmethod
    def create_contact(db: Session, contact: EmergencyContactCreate) -> EmergencyContact:
        """Create a new emergency contact."""
        existing_contacts = db.query(EmergencyContact).filter(EmergencyContact.user_id == contact.user_id).count()
        if existing_contacts >= 5:
            raise ValueError("A user can have a maximum of 5 emergency contacts.")
        db_contact = EmergencyContact(
            user_id=contact.user_id,
            name=contact.name,
            relation=contact.relation,
            phone=contact.phone
        )
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact

    @staticmethod
    def get_contact_by_id(db: Session, contact_id: int) -> Optional[EmergencyContact]:
        """Get an emergency contact by its ID."""
        return db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    @staticmethod
    def get_contacts_by_user(db: Session, user_id: int) -> List[EmergencyContact]:
        """Get all emergency contacts for a user."""
        return db.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).all()

    @staticmethod
    def update_contact(db: Session, contact_id: int, contact_update: EmergencyContactUpdate) -> Optional[EmergencyContact]:
        """Update an existing emergency contact."""
        db_contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        if not db_contact:
            return None
        update_data = contact_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_contact, field, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact

    @staticmethod
    def delete_contact(db: Session, contact_id: int) -> bool:
        """Delete an emergency contact by its ID."""
        db_contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        if not db_contact:
            return False
        db.delete(db_contact)
        db.commit()
        return True
