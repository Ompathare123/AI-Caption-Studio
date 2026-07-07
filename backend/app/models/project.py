import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String

from backend.app.database.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    name = Column(String(255), nullable=False, default="Untitled Project")
    is_favorite = Column(Boolean, nullable=False, default=False)
    captions_data = Column(JSON, nullable=False)
    style_data = Column(JSON, nullable=False)
    animation_preset = Column(
        String(50), nullable=False, default="word_highlight"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
