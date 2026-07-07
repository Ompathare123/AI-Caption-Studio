from typing import List
from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    audio_id: str = Field(
        ..., description="Unique identifier of the extracted audio track"
    )


class TranscriptionSegment(BaseModel):
    start: float = Field(..., description="Segment start time in seconds")
    end: float = Field(..., description="Segment end time in seconds")
    text: str = Field(..., description="Transcript text content of this segment")


class TranscriptionResponse(BaseModel):
    id: str = Field(..., description="Unique transcription run identifier")
    language: str = Field(
        ..., description="Detected language code (e.g., 'en')"
    )
    duration: float = Field(..., description="Total audio duration in seconds")
    processing_time: float = Field(
        ..., description="Transcription process computation duration in seconds"
    )
    segments: List[TranscriptionSegment] = Field(
        ..., description="Extracted timed segments of text"
    )
    status: str = Field(
        "completed", description="Final processing state status"
    )
