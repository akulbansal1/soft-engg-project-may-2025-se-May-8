from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.services.medicine_service import MedicineService
from src.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse
from src.utils.cache import Cache

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineResponse, responses={201: {"description": "Medicine created successfully."}, 400: {"description": "Invalid input."}})
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db)):
    """Create a new medicine record."""
    try:
        result = MedicineService.create_medicine(db, medicine)
        Cache.delete(f"medicines_user_{medicine.user_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/{user_id}", response_model=List[MedicineResponse], responses={200: {"description": "List of medicines for the user."}, 404: {"description": "User not found."}})
def get_medicines_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all medicines for a user."""
    cache_key = f"medicines_user_{user_id}"
    cached_medicines = Cache.get(cache_key)
    if cached_medicines:
        return cached_medicines
    medicines = MedicineService.get_medicines_by_user(db, user_id)
    medicines_data = [MedicineResponse.model_validate(med) for med in medicines]
    Cache.set(cache_key, [med.model_dump() for med in medicines_data], expiry=300)
    return medicines_data

@router.get("/{medicine_id}", response_model=MedicineResponse, responses={200: {"description": "Medicine found."}, 404: {"description": "Medicine not found."}})
def get_medicine_by_id(medicine_id: int, db: Session = Depends(get_db)):
    """Get a medicine by its ID."""
    medicine = MedicineService.get_medicine(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return medicine

@router.put("/{medicine_id}", response_model=MedicineResponse, responses={200: {"description": "Medicine updated successfully."}, 404: {"description": "Medicine not found."}})
def update_medicine(medicine_id: int, medicine_update: MedicineUpdate, db: Session = Depends(get_db)):
    """Update an existing medicine record."""
    medicine = MedicineService.update_medicine(db, medicine_id, medicine_update)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    Cache.delete(f"medicines_user_{medicine.user_id}")
    return medicine

@router.delete("/{medicine_id}", responses={200: {"description": "Medicine deleted successfully."}, 404: {"description": "Medicine not found."}})
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Delete a medicine by its ID."""
    medicine = MedicineService.get_medicine(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    success = MedicineService.delete_medicine(db, medicine_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    Cache.delete(f"medicines_user_{medicine.user_id}")
    return {"message": "Medicine deleted successfully"}
