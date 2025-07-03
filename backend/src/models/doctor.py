from sqlalchemy import Column, Integer, String
from src.db.database import Base

class Doctor(Base):
    """
    Doctor Model
    Fields: doctor_id, name, location
    """
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)

    def __repr__(self):
        return f"<Doctor(doctor_id={self.doctor_id}, name='{self.name}', location='{self.location}')>"
