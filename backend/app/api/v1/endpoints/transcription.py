from fastapi import APIRouter

from backend.app.schemas.transcription import (
    TranscriptionRequest,
    TranscriptionResponse,
)
from backend.app.services.transcription_service import TranscriptionService

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=200,
    summary="Transcribe audio to text",
    description=(
        "Loads the cached Faster-Whisper model and transcribes PCM mono "
        "16kHz WAV audio to text segments."
    ),
)
def transcribe_audio(payload: TranscriptionRequest):
    result = TranscriptionService.transcribe_audio(audio_id=payload.audio_id)
    return result
