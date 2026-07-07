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
    name: Optional[str] = Field(
        "Untitled Project", description="Custom name of the project"
    )


class ProjectUpdate(BaseModel):
    captions_data: Optional[List[Dict[str, Any]]] = Field(
        None, description="Complete segment and words timed sequence lists"
    )
    style_data: Optional[Dict[str, Any]] = Field(
        None, description="Visual captions style properties configs"
    )
    animation_preset: Optional[str] = Field(
        None, description="Visual animation preset configuration name"
    )
    name: Optional[str] = Field(None, description="Renamed project title")
    is_favorite: Optional[bool] = Field(
        None, description="Toggle favorite state"
    )


class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    video_id: str
    name: str
    is_favorite: bool
    captions_data: List[Dict[str, Any]]
    style_data: Dict[str, Any]
    animation_preset: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
