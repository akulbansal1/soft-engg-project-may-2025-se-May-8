from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.doctor import Doctor
from src.schemas.doctor import DoctorCreate, DoctorUpdate

class DoctorService:
    """Service class for Doctor CRUD operations."""

    @staticmethod
    def create_doctor(db: Session, doctor_in: DoctorCreate) -> Doctor:
        """Create a new doctor record."""
        doctor = Doctor(**doctor_in.model_dump())
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def get_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
        """Get a doctor by ID."""
        return db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()

    @staticmethod
    def get_all_doctors(db: Session) -> List[Doctor]:
        """Get all doctors."""
        return db.query(Doctor).all()

    @staticmethod
    def update_doctor(db: Session, doctor_id: int, doctor_in: DoctorUpdate) -> Optional[Doctor]:
        """Update a doctor record."""
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            return None
        for field, value in doctor_in.model_dump(exclude_unset=True).items():
            setattr(doctor, field, value)
        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def delete_doctor(db: Session, doctor_id: int) -> bool:
        """Delete a doctor record."""
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            return False
        db.delete(doctor)
        db.commit()
        return True
