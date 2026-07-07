from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from backend.app.services.project_service import ProjectService

router = APIRouter()


def check_project_permissions(project: Project, user: User):
    if project.user_id and project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project",
        )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize caption project session",
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService.create_project(
        db=db,
        video_id=payload.video_id,
        subtitle_id=payload.subtitle_id,
        user_id=current_user.id,
        name=payload.name,
    )


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Project).filter(Project.user_id == current_user.id).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectService.get_project(db=db, project_id=project_id)
    check_project_permissions(project, current_user)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectService.get_project(db=db, project_id=project_id)
    check_project_permissions(project, current_user)
    return ProjectService.update_project(
        db=db,
        project_id=project_id,
        captions_data=payload.captions_data,
        style_data=payload.style_data,
        animation_preset=payload.animation_preset,
        name=payload.name,
        is_favorite=payload.is_favorite,
    )


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectService.get_project(db=db, project_id=project_id)
    check_project_permissions(project, current_user)
    ProjectService.delete_project(db=db, project_id=project_id)
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/duplicate", response_model=ProjectResponse)
def duplicate_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectService.get_project(db=db, project_id=project_id)
    check_project_permissions(project, current_user)
    return ProjectService.duplicate_project(db=db, project_id=project_id)
