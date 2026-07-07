from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.subtitle import (
    SubtitleGenerateRequest,
    SubtitleGenerateResponse,
)
from backend.app.services.subtitle_service import SubtitleService

router = APIRouter()


@router.post(
    "/generate",
    response_model=SubtitleGenerateResponse,
    status_code=200,
    summary="Generate subtitle files",
    description=(
        "Fetches phonetic word timestamps and builds balanced SRT, "
        "ASS, and JSON files."
    ),
)
def generate_subtitles(
    payload: SubtitleGenerateRequest,
    db: Session = Depends(get_db),
):
    result = SubtitleService.generate_subtitles(
        db=db,
        alignment_id=payload.alignment_id,
        style=payload.style,
        max_words_per_line=payload.max_words_per_line,
        max_lines=payload.max_lines,
        output_formats=payload.output_formats,
    )
    return result
