import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    audio_id = Column(String(36), nullable=False)
    language = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    segments = relationship(
        "TranscriptSegment",
        back_populates="transcript",
        cascade="all, delete-orphan",
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(
        String(36), ForeignKey("transcripts.id"), nullable=False
    )
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)
    text = Column(String(1000), nullable=False)

    transcript = relationship("Transcript", back_populates="segments")
