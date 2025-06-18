from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.database import Base

class User(Base):
    """
    🔐 User Model
    
    Fields: id, name, phone, is_active, created_at
    Functions: user registration, login, logout, session issuing
    """
    __tablename__ = "users"

    # Primary fields as per UML schema
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(Integer, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    passkey_credentials = relationship("PasskeyCredential", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', phone='{self.phone}')>"
