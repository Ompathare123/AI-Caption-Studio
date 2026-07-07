from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.alignment import AlignmentRequest, AlignmentResponse
from backend.app.services.alignment_service import AlignmentService

router = APIRouter()


@router.post(
    "/align",
    response_model=AlignmentResponse,
    status_code=200,
    summary="Align transcript to audio",
    description=(
        "Loads the cached phonetic alignment model and computes exact "
        "word-level timestamps."
    ),
)
def align_transcript(
    payload: AlignmentRequest,
    db: Session = Depends(get_db),
):
    result = AlignmentService.align_transcript(
        db=db,
        audio_id=payload.audio_id,
        transcript_id=payload.transcript_id,
    )
    return result
