from fastapi import APIRouter, Depends, HTTPException, status
from src.api.constants import AUTH_ERROR_RESPONSES
from fastapi import Path
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.core.auth_middleware import RequireAdmin
from src.services.appointment_service import AppointmentService
from src.services.reminder_scheduler import ReminderService
from src.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post(
    "/",
    response_model=AppointmentResponse,
    responses={
        201: {"description": "Appointment created successfully."},
        400: {"description": "Invalid input."},
        **AUTH_ERROR_RESPONSES
    }
)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), isAdmin = Depends(RequireAdmin)):
    """
    Create a new appointment record for a user. Requires admin. Clears cache for the user and doctor.
    
    Supports US3 by enabling appointment management and reminders for users.
    """
    try:
        result = AppointmentService.create_appointment(db, appointment)

        ReminderService.auto_create_appointment_reminders(
            db, 
            appointment_id=result.id
        )
        
        Cache.delete(f"appointments_user_{appointment.user_id}")
        Cache.delete(f"appointments_doctor_{appointment.doctor_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AppointmentResponse], responses={200: {"description": "List of appointments for the user."}, 404: {"description": "User not found."}})
def get_appointments_by_user(
    user_id: int = Path(..., description="ID of the user to get appointments for"),
    db: Session = Depends(get_db)
):
    """
    List all appointments for a user. Results are cached for 5 minutes.
    
    Supports US3 and US7 by providing appointment lists for users and shared calendar access for families.
    """
    cache_key = f"appointments_user_{user_id}"
    cached_appointments = Cache.get(cache_key)
    if cached_appointments:
        return cached_appointments
    appointments = AppointmentService.get_appointments_by_user(db, user_id)
    
    appointments_data = []
    for app in appointments:
        app_dict = {
            "id": app.id,
            "name": app.name,
            "date": app.date,
            "time": app.time,
            "notes": app.notes,
            "user_id": app.user_id,
            "doctor_id": app.doctor_id,
            "medicines": [medicine.id for medicine in app.medicines] if app.medicines else None
        }
        appointments_data.append(AppointmentResponse.model_validate(app_dict))
    
    Cache.set(cache_key, [app.model_dump() for app in appointments_data], expiry=300)
    return appointments_data

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse], responses={200: {"description": "List of appointments for the doctor."}, 404: {"description": "Doctor not found."}})
def get_appointments_by_doctor(
    doctor_id: int = Path(..., description="ID of the doctor to get appointments for"),
    db: Session = Depends(get_db)
):
    """
    List all appointments for a doctor. Results are cached for 5 minutes.
    
    Supports US7 by enabling doctors and families to coordinate appointments.
    """
    cache_key = f"appointments_doctor_{doctor_id}"
    cached_appointments = Cache.get(cache_key)
    if cached_appointments:
        return cached_appointments
    appointments = AppointmentService.get_appointments_by_doctor(db, doctor_id)
    
    appointments_data = []
    for app in appointments:
        app_dict = {
            "id": app.id,
            "name": app.name,
            "date": app.date,
            "time": app.time,
            "notes": app.notes,
            "user_id": app.user_id,
            "doctor_id": app.doctor_id,
            "medicines": [medicine.id for medicine in app.medicines] if app.medicines else None
        }
        appointments_data.append(AppointmentResponse.model_validate(app_dict))
    
    Cache.set(cache_key, [app.model_dump() for app in appointments_data], expiry=300)
    return appointments_data

@router.get("/{appointment_id}", response_model=AppointmentResponse, responses={200: {"description": "Appointment found."}, 404: {"description": "Appointment not found."}})
def get_appointment_by_id(
    appointment_id: int = Path(..., description="ID of the appointment to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get an appointment by its ID.
    
    Supports US3 by allowing users and caregivers to review appointment details.
    """
    appointment = AppointmentService.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    responses={
        200: {"description": "Appointment updated successfully."},
        404: {"description": "Appointment not found."},
        **AUTH_ERROR_RESPONSES
    }
)
def update_appointment(
    appointment_id: int = Path(..., description="ID of the appointment to update"),
    appointment_update: AppointmentUpdate = None,
    db: Session = Depends(get_db),
    isAdmin = Depends(RequireAdmin)
):
    """
    Update an existing appointment record. Requires admin. Clears cache for the user and doctor.
    
    Supports US3 by keeping appointment records up to date for users and families.
    """
    appointment = AppointmentService.update_appointment(db, appointment_id, appointment_update)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    # Invalidate caches
    Cache.delete(f"appointments_user_{appointment.user_id}")
    Cache.delete(f"appointments_doctor_{appointment.doctor_id}")
    return appointment

@router.delete(
    "/{appointment_id}",
    responses={
        200: {"description": "Appointment deleted successfully."},
        404: {"description": "Appointment not found."},
        **AUTH_ERROR_RESPONSES
    }
)
def delete_appointment(
    appointment_id: int = Path(..., description="ID of the appointment to delete"),
    db: Session = Depends(get_db),
    isAdmin = Depends(RequireAdmin)
):
    """
    Delete an appointment record by ID. Requires admin. Clears cache for the user and doctor.
    
    Supports US3 by allowing removal of outdated or incorrect appointments.
    """
    appointment = AppointmentService.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    success = AppointmentService.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    # Invalidate caches
    Cache.delete(f"appointments_user_{appointment.user_id}")
    Cache.delete(f"appointments_doctor_{appointment.doctor_id}")
    return {"message": "Appointment deleted successfully"}
