from fastapi import APIRouter, Depends, HTTPException, status
from src.api.constants import AUTH_ERROR_RESPONSES
from fastapi import Query, Path
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.db.database import get_db
from src.services.user_service import UserService
from src.services.emergency_contact_service import EmergencyContactService
from src.services.reminder_service import ReminderService
from src.services.sms_service import get_sms_service
from src.schemas.user import  UserResponse, UserSession
from src.schemas.sos import SOSResponse, SOSRequest
from src.schemas.reminder import ReminderResponse

from src.core.auth_middleware import RequireAuth, RequireOwnership, RequireAdminOrUser

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/",
    response_model=List[UserResponse],
    responses={
        **AUTH_ERROR_RESPONSES
    }
)
def get_users(
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of users to return"),
    db: Session = Depends(get_db),
    current_user = Depends(RequireAdminOrUser)
):
    """
    List all users. Returns a paginated list. Requires authentication. Results are cached for 5 minutes.
    """
    users = UserService.get_users(db, skip=skip, limit=limit)
    users_data = [UserResponse.model_validate(user) for user in users]
    return users_data

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        **AUTH_ERROR_RESPONSES
    }
)
def get_user(
    user_id: int = Path(..., description="ID of the user to retrieve"),
    db: Session = Depends(get_db),
    user = Depends(RequireOwnership)
):
    """
    Get a user by ID. Only the user or an admin can access this endpoint.
    
    Supports US11 by allowing users and doctors to review user profiles and history.
    """
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.post(
    "/{user_id}/sos/trigger",
    response_model=SOSResponse,
    responses={
        **AUTH_ERROR_RESPONSES
    }
)
def trigger_sos(
    user_id: int, 
    request: SOSRequest,
    db: Session = Depends(get_db), 
    current_user = Depends(RequireOwnership)
):
    """
    Trigger an SOS alert for a user. Sends emergency SMS messages to all of the user's registered emergency contacts. Only the user can trigger this. Returns the number of contacts notified and any failures.
    
    Supports US4 by providing an emergency alert system for users living alone.
    """
    
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
            result = sms_service.send_emergency_message(
                contact.phone, 
                user_name, 
                location=request.location
            )
            if result['success']:
                contacts_notified += 1
        except Exception as e:
            failed_notifications.append(contact.phone)
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

@router.get(
    "/{user_id}/reminders",
    response_model=List[ReminderResponse],
    responses={
        **AUTH_ERROR_RESPONSES
    }
)
def get_user_reminders(
    user_id: int = Path(..., description="ID of the user to get reminders for"),
    include_inactive: bool = Query(False, description="Whether to include inactive/cancelled reminders"),
    limit: int = Query(100, description="Maximum number of reminders to return"),
    skip: int = Query(0, description="Number of reminders to skip for pagination"),
    db: Session = Depends(get_db),
    user = Depends(RequireOwnership)
):
    """
    Get all reminders for a user. Returns past, current and future reminders.
    Only the user can access their own reminders.
    
    Query parameters:
    - include_inactive: Include cancelled/inactive reminders (default: false)
    - limit: Maximum number of results (default: 100)
    - skip: Number of results to skip for pagination (default: 0)
    """
    reminders = ReminderService.get_reminders_by_user(
        db, 
        user_id, 
        include_inactive=include_inactive
    )
    
    paginated_reminders = reminders[skip:skip + limit]
    
    return [ReminderResponse.model_validate(reminder) for reminder in paginated_reminders]

@router.get(
    "/{user_id}/reminders/past",
    response_model=List[ReminderResponse],
    responses={
        **AUTH_ERROR_RESPONSES
    }
)
def get_user_past_reminders(
    user_id: int = Path(..., description="ID of the user to get pending reminders for"),
    limit: int = Query(50, description="Maximum number of reminders to return"),
    db: Session = Depends(get_db),
    user = Depends(RequireOwnership)
):
    """
    Get only past reminders for a user, that have already occurred.
    Only the user can access their own reminders.
    """
    reminders = ReminderService.get_reminders_by_user(
        db, 
        user_id
    )

    reminders = [rem for rem in reminders if rem.scheduled_time < datetime.now() and rem.is_active]
    
    limited_reminders = reminders[:limit]
    
    return [ReminderResponse.model_validate(reminder) for reminder in limited_reminders]