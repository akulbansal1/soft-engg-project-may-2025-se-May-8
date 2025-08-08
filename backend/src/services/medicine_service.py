from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.medicine import Medicine
from src.schemas.medicine import MedicineCreate, MedicineUpdate

class MedicineService:
    """Service class for Medicine CRUD operations."""

    @staticmethod
    def create_medicine(db: Session, medicine_in: MedicineCreate) -> Medicine:
        """Create a new medicine record."""
        medicine = Medicine(**medicine_in.model_dump())
        db.add(medicine)
        db.commit()
        db.refresh(medicine)
        return medicine

    @staticmethod
    def get_medicine(db: Session, medicine_id: int) -> Optional[Medicine]:
        """Get a medicine by its ID."""
        return db.query(Medicine).filter(Medicine.id == medicine_id).first()

    @staticmethod
    def get_medicines_by_user(db: Session, user_id: int) -> List[Medicine]:
        """Get all medicines for a user."""
        return db.query(Medicine).filter(Medicine.user_id == user_id).all()

    @staticmethod
    def update_medicine(db: Session, medicine_id: int, medicine_in: MedicineUpdate) -> Optional[Medicine]:
        """Update a medicine record."""
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            return None
        for field, value in medicine_in.model_dump(exclude_unset=True).items():
            setattr(medicine, field, value)
        db.commit()
        db.refresh(medicine)
        return medicine

    @staticmethod
    def delete_medicine(db: Session, medicine_id: int) -> bool:
        """Delete a medicine record."""
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            return False
        db.delete(medicine)
        db.commit()
        return True
