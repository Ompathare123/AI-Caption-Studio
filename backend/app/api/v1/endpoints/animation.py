from typing import List

from fastapi import APIRouter

from backend.app.schemas.animation import (
    ApplyAnimationRequest,
    ApplyAnimationResponse,
)
from backend.app.services.animation_service import AnimationService

router = APIRouter()


@router.get(
    "",
    response_model=List[str],
    summary="List available caption animations",
    description="Returns names of all supported visual animation preset profiles.",
)
def list_animations():
    return AnimationService.list_animations()


@router.post(
    "/apply",
    response_model=ApplyAnimationResponse,
    summary="Apply animation keyframe sequence to subtitles",
    description=(
        "Parses alignment timestamps, applies selected preset styling features, "
        "and computes detailed absolute timeline keyframes."
    ),
)
def apply_animation(payload: ApplyAnimationRequest):
    # Convert subtitles Pydantic structure to raw dictionary list
    subtitles_dict = [seg.model_dump() for seg in payload.subtitles]
    result = AnimationService.apply_animation(
        subtitles=subtitles_dict,
        style=payload.style,
        preset=payload.animation_preset,
    )
    return result
