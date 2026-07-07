from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.v1.endpoints.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.name is not None:
        current_user.name = payload.name
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.language is not None:
        current_user.language = payload.language
    if payload.timezone is not None:
        current_user.timezone = payload.timezone

    db.commit()
    db.refresh(current_user)
    return current_user
