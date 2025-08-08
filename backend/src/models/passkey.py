from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.database import Base

class PasskeyCredential(Base):
    """
    🔐 PasskeyCredential Model
    
    Fields: id, user_id, credential_id, public_key, sign_count, created_at
    """
    __tablename__ = "passkey_credentials"

    # Primary fields as per UML schema
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(String, unique=True, nullable=False, index=True)
    public_key = Column(Text, nullable=False)
    sign_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to User model
    user = relationship("User", back_populates="passkey_credentials")

    def __repr__(self):
        return f"<PasskeyCredential(id={self.id}, user_id={self.user_id}, credential_id='{self.credential_id[:8]}...')>"
