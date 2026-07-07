from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.audio import AudioExtractRequest, AudioExtractResponse
from backend.app.services.audio_service import AudioService

router = APIRouter()


@router.post(
    "/extract",
    response_model=AudioExtractResponse,
    status_code=200,
    summary="Extract audio from a video",
    description="Extracts audio from an uploaded video using FFmpeg and converts it to PCM mono 16kHz WAV format.",
)
def extract_audio(
    payload: AudioExtractRequest,
    db: Session = Depends(get_db),
):
    result = AudioService.extract_audio(db=db, video_id=payload.video_id)
    return result
