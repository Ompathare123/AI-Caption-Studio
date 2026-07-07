from fastapi import APIRouter
from backend.app.api.v1.endpoints.upload import router as upload_router
from backend.app.api.v1.endpoints.audio import router as audio_router
from backend.app.api.v1.endpoints.transcription import router as transcription_router
from backend.app.api.v1.endpoints.alignment import router as alignment_router
from backend.app.api.v1.endpoints.subtitle import router as subtitle_router
from backend.app.api.v1.endpoints.caption_style import router as caption_style_router
from backend.app.api.v1.endpoints.animation import router as animation_router

api_router = APIRouter()
api_router.include_router(upload_router, tags=["upload"])
api_router.include_router(audio_router, prefix="/audio", tags=["audio"])
api_router.include_router(transcription_router, tags=["transcription"])
api_router.include_router(alignment_router, tags=["alignment"])
api_router.include_router(subtitle_router, prefix="/subtitles", tags=["subtitles"])
api_router.include_router(caption_style_router, prefix="/styles", tags=["styles"])
api_router.include_router(animation_router, prefix="/animations", tags=["animations"])
