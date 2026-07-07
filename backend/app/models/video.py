import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from backend.app.database.session import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)
