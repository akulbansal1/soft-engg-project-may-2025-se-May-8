from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated

from src.db.database import get_db
from src.core.auth_middleware import RequireAdminOrOwnership, RequireAdminOrUser
from src.services.emergency_contact_service import EmergencyContactService
from src.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate, EmergencyContactResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/emergency-contacts", tags=["Emergency Contacts"])

@router.post("/", response_model=EmergencyContactResponse, responses={201: {"description": "Emergency contact created successfully."}, 400: {"description": "Invalid input or maximum contacts reached (5)."}})
def create_contact(
    contact: EmergencyContactCreate, 
    db: Session = Depends(get_db), 
    session_token: Annotated[Optional[str], Cookie()] = None
):
    """Create a new emergency contact."""
    RequireAdminOrUser(user_id=contact.user_id,session_token=session_token, db=db)
    
    # Enforce max 5 contacts per user
    existing_contacts = EmergencyContactService.get_contacts_by_user(db, contact.user_id)
    if len(existing_contacts) >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum of 5 emergency contacts allowed per user.")
    try:
        result = EmergencyContactService.create_contact(db, contact)
        # Clear cache for this user's contacts
        Cache.delete(f"emergency_contacts_user_{contact.user_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/{user_id}", response_model=List[EmergencyContactResponse], responses={200: {"description": "List of emergency contacts for the user."}, 404: {"description": "User not found."}})
def get_contacts_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all emergency contacts for a user."""
    cache_key = f"emergency_contacts_user_{user_id}"
    cached_contacts = Cache.get(cache_key)
    if cached_contacts:
        return cached_contacts
    contacts = EmergencyContactService.get_contacts_by_user(db, user_id)
    contacts_data = [EmergencyContactResponse.model_validate(contact) for contact in contacts]
    Cache.set(cache_key, [contact.model_dump() for contact in contacts_data], expiry=300)
    return contacts_data

@router.get("/{contact_id}", response_model=EmergencyContactResponse, responses={200: {"description": "Emergency contact found."}, 404: {"description": "Contact not found."}})
def get_contact_by_id(contact_id: int, db: Session = Depends(get_db)):
    """Get an emergency contact by its ID."""
    contact = EmergencyContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=EmergencyContactResponse, responses={200: {"description": "Emergency contact updated successfully."}, 404: {"description": "Contact not found."}})
def update_contact(contact_id: int, contact_update: EmergencyContactUpdate, db: Session = Depends(get_db), isAuthenticated: bool = Depends(RequireAdminOrOwnership)):
    """Update an existing emergency contact."""
    contact = EmergencyContactService.update_contact(db, contact_id, contact_update)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # Clear cache for this user's contacts
    Cache.delete(f"emergency_contacts_user_{contact.user_id}")
    return contact

@router.delete("/{contact_id}", responses={200: {"description": "Emergency contact deleted successfully."}, 404: {"description": "Contact not found."}})
def delete_contact(contact_id: int, db: Session = Depends(get_db), isAuthenticated: bool = Depends(RequireAdminOrOwnership)):
    """Delete an emergency contact by its ID."""
    contact = EmergencyContactService.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    success = EmergencyContactService.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    # Clear cache for this user's contacts
    Cache.delete(f"emergency_contacts_user_{contact.user_id}")
    return {"message": "Contact deleted successfully"}
