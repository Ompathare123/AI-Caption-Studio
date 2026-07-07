from typing import List, Optional
from pydantic import BaseModel, Field


class AlignmentRequest(BaseModel):
    audio_id: str = Field(
        ..., description="Unique UUID of the extracted audio WAV file"
    )
    transcript_id: str = Field(
        ..., description="Unique UUID of the stored database transcript record"
    )


class AlignedWord(BaseModel):
    word: str = Field(..., description="The spoken word text")
    start: Optional[float] = Field(
        None, description="Start timestamp of the word in seconds"
    )
    end: Optional[float] = Field(
        None, description="End timestamp of the word in seconds"
    )
    confidence: Optional[float] = Field(
        None,
        description="WhisperX alignment confidence score (0.0 to 1.0) if successfully aligned",
    )


class AlignmentResponse(BaseModel):
    id: str = Field(..., description="Unique alignment process run identifier")
    language: str = Field(
        ..., description="Transcription and alignment language code"
    )
    duration: float = Field(..., description="Total audio duration in seconds")
    words: List[AlignedWord] = Field(
        ..., description="Phonetically aligned word-level timestamps"
    )
    status: str = Field(
        "completed", description="Final processing state status"
    )
