from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Text
from sqlalchemy.orm import relationship
from src.db.database import Base

class Appointment(Base):
    """
    Appointment Model
    Fields: id, user_id, doctor_id, name, date, time, notes
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref="appointments")
    doctor = relationship("Doctor", backref="appointments")
    medicines = relationship("Medicine", back_populates="appointment")

    def __repr__(self):
        return f"<Appointment(id={self.id}, user_id={self.user_id}, doctor_id={self.doctor_id}, name='{self.name}')>"
