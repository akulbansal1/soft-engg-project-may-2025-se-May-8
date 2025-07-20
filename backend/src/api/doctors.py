from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.core.auth_middleware import RequireAdmin
from src.services.doctor_service import DoctorService
from src.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/", response_model=DoctorResponse, responses={201: {"description": "Doctor created successfully."}, 400: {"description": "Invalid input."}})
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    isAdmin = Depends(RequireAdmin)
):
    """
    Create a new doctor record. Requires admin authentication. Clears doctors cache.
    """
    try:
        result = DoctorService.create_doctor(db, doctor)
        # Invalidate all doctors cache
        Cache.delete("doctors_all")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[DoctorResponse], responses={200: {"description": "List of all doctors."}})
def get_all_doctors(db: Session = Depends(get_db)):
    """
    Get all doctors. Results are cached for 5 minutes.
    """
    cache_key = "doctors_all"
    cached_doctors = Cache.get(cache_key)
    if cached_doctors:
        return cached_doctors
    doctors = DoctorService.get_all_doctors(db)
    doctors_data = [DoctorResponse.model_validate(doc) for doc in doctors]
    Cache.set(cache_key, [doc.model_dump() for doc in doctors_data], expiry=300)
    return doctors_data

@router.get("/{doctor_id}", response_model=DoctorResponse, responses={200: {"description": "Doctor found."}, 404: {"description": "Doctor not found."}})
def get_doctor_by_id(
    doctor_id: int = Path(..., description="ID of the doctor to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get a doctor by ID. Results are cached for 5 minutes.
    """
    cache_key = f"doctor_{doctor_id}"
    cached_doctor = Cache.get(cache_key)
    if cached_doctor:
        return cached_doctor
    doctor = DoctorService.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    doctor_data = DoctorResponse.model_validate(doctor)
    Cache.set(cache_key, doctor_data.model_dump(), expiry=300)
    return doctor_data

@router.put("/{doctor_id}", response_model=DoctorResponse, responses={200: {"description": "Doctor updated successfully."}, 404: {"description": "Doctor not found."}})
def update_doctor(
    doctor_id: int = Path(..., description="ID of the doctor to update"),
    doctor_update: DoctorUpdate = ...,
    db: Session = Depends(get_db),
    isAdmin = Depends(RequireAdmin)
):
    """
    Update an existing doctor record. Requires admin authentication. Clears doctors cache.
    """
    doctor = DoctorService.update_doctor(db, doctor_id, doctor_update)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    # Invalidate caches
    Cache.delete("doctors_all")
    Cache.delete(f"doctor_{doctor_id}")
    return doctor

@router.delete("/{doctor_id}", responses={200: {"description": "Doctor deleted successfully."}, 404: {"description": "Doctor not found."}})
def delete_doctor(
    doctor_id: int = Path(..., description="ID of the doctor to delete"),
    db: Session = Depends(get_db),
    isAdmin = Depends(RequireAdmin)
):
    """
    Delete a doctor by ID. Requires admin authentication. Clears doctors cache.
    """
    doctor = DoctorService.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    success = DoctorService.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    # Invalidate caches
    Cache.delete("doctors_all")
    Cache.delete(f"doctor_{doctor_id}")
    return {"message": "Doctor deleted successfully"}
