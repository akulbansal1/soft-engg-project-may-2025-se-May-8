from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.db.database import Base

class User(Base):
    """
    🔐 User Model
    
    Fields: id, name, email, created_at
    Functions: user registration, login, logout, session issuing
    """
    __tablename__ = "users"

    # Primary fields as per UML schema
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
