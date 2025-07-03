from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.appointment import Appointment
from src.schemas.appointment import AppointmentCreate, AppointmentUpdate
from src.models.medicine import Medicine

class AppointmentService:
    """Service class for Appointment CRUD operations."""

    @staticmethod
    def create_appointment(db: Session, appointment_in: AppointmentCreate) -> Appointment:
        """Create a new appointment record."""
        appointment = Appointment(**appointment_in.model_dump())
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
        """Get an appointment by ID."""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    @staticmethod
    def get_appointments_by_user(db: Session, user_id: int) -> List[Appointment]:
        """Get all appointments for a user."""
        return db.query(Appointment).filter(Appointment.user_id == user_id).all()

    @staticmethod
    def get_appointments_by_doctor(db: Session, doctor_id: int) -> List[Appointment]:
        """Get all appointments for a doctor."""
        return db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()

    @staticmethod
    def update_appointment(db: Session, appointment_id: int, appointment_in: AppointmentUpdate) -> Optional[Appointment]:
        """Update an appointment record."""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return None
        for field, value in appointment_in.model_dump(exclude_unset=True).items():
            setattr(appointment, field, value)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def delete_appointment(db: Session, appointment_id: int) -> bool:
        """Delete an appointment record."""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False
        db.delete(appointment)
        db.commit()
        return True
