from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.render import RenderRequest, RenderStatusResponse
from backend.app.services.render_service import RenderService

router = APIRouter()


@router.post(
    "",
    response_model=RenderStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger caption video rendering task",
    description=(
        "Validates source tracks database registrations, triggers background "
        "compositor rendering threads, and returns tracking status parameters."
    ),
)
def start_render(payload: RenderRequest, db: Session = Depends(get_db)):
    render_id = RenderService.start_render_job(
        db=db,
        video_id=payload.video_id,
        subtitle_id=payload.subtitle_id,
        style_name=payload.style_name,
        animation_preset=payload.animation_preset,
    )
    status_data = RenderService.get_render_status(render_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate background rendering task",
        )
    return status_data


@router.get(
    "/{render_id}",
    response_model=RenderStatusResponse,
    summary="Retrieve caption rendering task status",
    description=(
        "Check status flags and current rendering progress percentage levels."
    ),
)
def get_render_status(render_id: str):
    status_data = RenderService.get_render_status(render_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job '{render_id}' not found in active tracking cache",
        )
    return status_data
