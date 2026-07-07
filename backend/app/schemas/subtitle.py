from typing import Dict, List
from pydantic import BaseModel, Field


class SubtitleGenerateRequest(BaseModel):
    alignment_id: str = Field(
        ..., description="Unique UUID of the database alignment record"
    )
    style: str = Field(
        "default", description="Subtitle presentation style definition key"
    )
    max_words_per_line: int = Field(
        5,
        description="Maximum words allowed on a single line of text",
        ge=1,
        le=20,
    )
    max_lines: int = Field(
        2,
        description="Maximum caption lines allowed on screen simultaneously",
        ge=1,
        le=5,
    )
    output_formats: List[str] = Field(
        default=["json", "srt", "ass"],
        description="List of target subtitle formats to generate",
    )


class SubtitleGenerateResponse(BaseModel):
    id: str = Field(
        ..., description="Unique subtitle generation process run identifier"
    )
    subtitle_files: Dict[str, str] = Field(
        ..., description="Map of format extensions to generated absolute paths"
    )
    caption_count: int = Field(
        ..., description="Total count of caption block segments generated"
    )
    status: str = Field(
        "completed", description="Final processing state status"
    )
