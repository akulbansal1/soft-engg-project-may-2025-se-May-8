from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.appointment_service import AppointmentService
from src.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentResponse, responses={201: {"description": "Appointment created successfully."}, 400: {"description": "Invalid input."}})
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Create a new appointment record."""
    try:
        result = AppointmentService.create_appointment(db, appointment)
        Cache.delete(f"appointments_user_{appointment.user_id}")
        Cache.delete(f"appointments_doctor_{appointment.doctor_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/{user_id}", response_model=List[AppointmentResponse], responses={200: {"description": "List of appointments for the user."}, 404: {"description": "User not found."}})
def get_appointments_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all appointments for a user."""
    cache_key = f"appointments_user_{user_id}"
    cached_appointments = Cache.get(cache_key)
    if cached_appointments:
        return cached_appointments
    appointments = AppointmentService.get_appointments_by_user(db, user_id)
    appointments_data = [AppointmentResponse.model_validate(app) for app in appointments]
    Cache.set(cache_key, [app.model_dump() for app in appointments_data], expiry=300)
    return appointments_data

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse], responses={200: {"description": "List of appointments for the doctor."}, 404: {"description": "Doctor not found."}})
def get_appointments_by_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get all appointments for a doctor."""
    cache_key = f"appointments_doctor_{doctor_id}"
    cached_appointments = Cache.get(cache_key)
    if cached_appointments:
        return cached_appointments
    appointments = AppointmentService.get_appointments_by_doctor(db, doctor_id)
    appointments_data = [AppointmentResponse.model_validate(app) for app in appointments]
    Cache.set(cache_key, [app.model_dump() for app in appointments_data], expiry=300)
    return appointments_data

@router.get("/{appointment_id}", response_model=AppointmentResponse, responses={200: {"description": "Appointment found."}, 404: {"description": "Appointment not found."}})
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):
    """Get an appointment by its ID."""
    appointment = AppointmentService.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse, responses={200: {"description": "Appointment updated successfully."}, 404: {"description": "Appointment not found."}})
def update_appointment(appointment_id: int, appointment_update: AppointmentUpdate, db: Session = Depends(get_db)):
    """Update an existing appointment record."""
    appointment = AppointmentService.update_appointment(db, appointment_id, appointment_update)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    # Invalidate caches
    Cache.delete(f"appointments_user_{appointment.user_id}")
    Cache.delete(f"appointments_doctor_{appointment.doctor_id}")
    return appointment

@router.delete("/{appointment_id}", responses={200: {"description": "Appointment deleted successfully."}, 404: {"description": "Appointment not found."}})
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Delete an appointment by its ID."""
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
