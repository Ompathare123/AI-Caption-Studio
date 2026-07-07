from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    video_id: str = Field(
        ..., description="Unique UUID reference of the source video"
    )
    subtitle_id: Optional[str] = Field(
        None,
        description="Optional subtitle ID to pre-populate timeline alignments",
    )


class ProjectUpdate(BaseModel):
    captions_data: List[Dict[str, Any]] = Field(
        ..., description="Complete segment and words timed sequence lists"
    )
    style_data: Dict[str, Any] = Field(
        ..., description="Visual captions style properties configs"
    )
    animation_preset: str = Field(
        "word_highlight", description="Visual animation preset configuration name"
    )


class ProjectResponse(BaseModel):
    id: str
    video_id: str
    captions_data: List[Dict[str, Any]]
    style_data: Dict[str, Any]
    animation_preset: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
