from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from src.db.database import Base

class Medicine(Base):
    """
    Medicine Model
    Fields: id, user_id, doctor_id, name, dosage, frequency, start_date, end_date, notes
    """
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="medicines")
    appointment = relationship("Appointment", back_populates="medicines")
    doctor = relationship("Doctor", backref="medicines")

    def __repr__(self):
        return f"<Medicine(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

    def __str__(self):
        return (
            f"Medicine(\n"
            f"  id={self.id},\n"
            f"  user_id={self.user_id},\n"
            f"  doctor_id={self.doctor_id},\n"
            f"  appointment_id={self.appointment_id},\n"
            f"  name='{self.name}',\n"
            f"  dosage='{self.dosage}',\n"
            f"  frequency='{self.frequency}',\n"
            f"  start_date={self.start_date},\n"
            f"  end_date={self.end_date},\n"
            f"  notes='{self.notes}'\n"
            f")"
        )
