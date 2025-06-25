from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.db.database import Base
from datetime import datetime, timezone

class Document(Base):
    """
    Document Model
    Fields: id, user_id, name, file_url, timestamp
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship(
        "User",
        backref="documents"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
