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
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="medicines")
    appointment = relationship("Appointment", back_populates="medicines")

    def __repr__(self):
        return f"<Medicine(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
