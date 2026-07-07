from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.upload import VideoUploadResponse
from backend.app.services.upload_service import UploadService

router = APIRouter()


@router.post(
    "/upload",
    response_model=VideoUploadResponse,
    status_code=201,
    summary="Upload a video file",
    description="Upload a video, validate size/format, check for corruption and duplicates, and save metadata.",
)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload"),
    db: Session = Depends(get_db),
):
    video = await UploadService.process_upload(db=db, file=file)
    return video
