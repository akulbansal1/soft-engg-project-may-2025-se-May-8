from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.user_service import UserService
from src.services.emergency_contact_service import EmergencyContactService
from src.services.sms_service import get_sms_service
from src.schemas.user import  UserResponse, UserSession
from src.schemas.sos import SOSResponse

from src.core.auth_middleware import RequireAuth, RequireOwnership

router = APIRouter(prefix="/users", tags=["🔐 Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(RequireAuth)):
    """Get all users with caching"""
    
    # Get from database
    users = UserService.get_users(db, skip=skip, limit=limit)
    
    # Convert to response format and cache for 5 minutes
    users_data = [UserResponse.model_validate(user) for user in users]

    return users_data

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), user = Depends(RequireOwnership)):
    """Get user by ID"""
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.post("/{user_id}/sos/trigger", response_model=SOSResponse)
def trigger_sos(user_id: int, db: Session = Depends(get_db), current_user = Depends(RequireOwnership)):
    """Trigger SOS - Send emergency messages to all emergency contacts"""
    
    # Get the user's emergency contacts
    emergency_contacts = EmergencyContactService.get_contacts_by_user(db, user_id)
    
    if not emergency_contacts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No emergency contacts found. Please add emergency contacts before using SOS."
        )
    
    # Get SMS service
    sms_service = get_sms_service()
    
    user_name = getattr(current_user, 'name', None) or getattr(current_user, 'email', 'Someone')
    
    # Send emergency messages to all contacts
    contacts_notified = 0
    failed_notifications = []
    
    for contact in emergency_contacts:
        try:
            result = sms_service.send_emergency_message(contact.phone, user_name)
            if result['success']:
                contacts_notified += 1
        except Exception as e:
            failed_notifications.append(contact.phone)
            # Log the error but continue with other contacts
            print(f"Failed to send SOS to {contact.phone}: {str(e)}")
    
    # Determine overall success
    success = contacts_notified > 0
    
    if success:
        message = f"Emergency SOS triggered! {contacts_notified} emergency contact(s) have been notified."
        if failed_notifications:
            message += f" {len(failed_notifications)} notification(s) failed."
    else:
        message = "Failed to send SOS messages to any emergency contacts."
    
    return SOSResponse(
        success=success,
        message=message,
        contacts_notified=contacts_notified,
        failed_notifications=failed_notifications
    )

## TODO: Implement this endpoint properly with the right authentication setting
# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     """Update user information"""
#     updated_user = UserService.update_user(db, user_id, user_update)
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Clear cache
#     Cache.clear_pattern("users_list_*")
    
#     return updated_user