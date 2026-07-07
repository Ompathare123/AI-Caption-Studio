from typing import Optional
from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    video_id: str = Field(
        ..., description="Unique UUID of the uploaded video record"
    )
    subtitle_id: str = Field(
        ..., description="Unique UUID of the generated subtitle task"
    )
    style_name: str = Field(
        "default",
        description="Style name config preset to apply (e.g. 'tiktok')",
    )
    animation_preset: str = Field(
        "word_highlight",
        description="Animation preset name config (e.g. 'word_pop')",
    )


class RenderStatusResponse(BaseModel):
    render_id: str = Field(
        ..., description="Unique UUID tracking this rendering job task"
    )
    status: str = Field(
        ...,
        description="Current job status: processing, rendering, completed, failed",
    )
    progress: int = Field(
        ..., description="Rendering progress percentage status", ge=0, le=100
    )
    output_path: Optional[str] = Field(
        None, description="Absolute file path of the final rendered video"
    )
    error_message: Optional[str] = Field(
        None, description="Detailed error description if rendering failed"
    )
