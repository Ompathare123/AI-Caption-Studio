from typing import List

from fastapi import APIRouter, Body

from backend.app.schemas.caption_style import (
    ApplyStyleRequest,
    ApplyStyleResponse,
    StyleProperties,
)
from backend.app.services.caption_style_service import CaptionStyleService

router = APIRouter()


@router.get(
    "",
    response_model=List[str],
    summary="List available caption styles",
    description="Scans predefined and custom style folders and returns all available style names.",
)
def list_styles():
    return CaptionStyleService.list_styles()


@router.post(
    "/apply",
    response_model=ApplyStyleResponse,
    summary="Apply style properties and text effects to subtitles",
    description=(
        "Loads the styling presets, scales outline/margins/font sizes "
        "responsively to resolution, and transforms text casings/emojis."
    ),
)
def apply_style(payload: ApplyStyleRequest):
    # Convert Pydantic structures to dictionary list
    subtitles_dict = [seg.model_dump() for seg in payload.subtitles]
    result = CaptionStyleService.apply_style(
        subtitles=subtitles_dict,
        style_name=payload.style_name,
        width=payload.width,
        height=payload.height,
        aspect_ratio=payload.aspect_ratio,
    )
    return result


@router.post(
    "/custom",
    status_code=201,
    summary="Save a new custom style config",
    description=(
        "Validates style properties and writes a custom JSON style sheet "
        "to custom/ directory."
    ),
)
def create_custom_style(
    style_name: str = Body(..., embed=True),
    style_properties: StyleProperties = Body(...),
):
    filepath = CaptionStyleService.create_custom_style(
        style_name=style_name,
        style_data=style_properties.model_dump(),
    )
    return {
        "message": f"Custom style '{style_name}' created successfully",
        "filepath": filepath,
    }
