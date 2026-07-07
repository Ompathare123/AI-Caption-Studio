import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from backend.app.database.session import Base


class Alignment(Base):
    __tablename__ = "alignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcript_id = Column(
        String(36), ForeignKey("transcripts.id"), nullable=False
    )
    audio_id = Column(String(36), nullable=False)
    language = Column(String(10), nullable=False)
    duration = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="completed")
    words_json = Column(String, nullable=False)  # Serialized list of aligned words
    created_at = Column(DateTime, default=datetime.utcnow)
