from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from backend.app.services.project_service import ProjectService

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize caption project session",
    description=(
        "Validates tracks database registration, reads initial alignment segments, "
        "and creates database project records."
    ),
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(
        db=db, video_id=payload.video_id, subtitle_id=payload.subtitle_id
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Load project configuration",
    description="Loads timed captions timeline lists and styles properties parameters.",
)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return ProjectService.get_project(db=db, project_id=project_id)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Save project configuration modifications",
    description=(
        "Saves segment edits, timings shifts, visual styles, and animation presets."
    ),
)
def update_project(
    project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)
):
    return ProjectService.update_project(
        db=db,
        project_id=project_id,
        captions_data=payload.captions_data,
        style_data=payload.style_data,
        animation_preset=payload.animation_preset,
    )
