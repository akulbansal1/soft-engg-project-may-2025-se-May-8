from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.db.database import Base

class EmergencyContact(Base):
    """
    EmergencyContact Model
    Fields: id, user_id, name, relation, phone
    Note: A user can have a maximum of 5 emergency contacts.
    """
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    relation = Column(String, nullable=True)
    phone = Column(Integer, nullable=False)

    # Relationship to User model
    user = relationship("User", back_populates="emergency_contacts")

    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
