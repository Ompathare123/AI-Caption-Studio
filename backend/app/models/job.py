import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from backend.app.database.session import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")
    progress = Column(Integer, nullable=False, default=0)
    current_step = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
