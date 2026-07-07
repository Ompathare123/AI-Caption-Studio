from fastapi import APIRouter
from backend.app.api.v1.endpoints.upload import router as upload_router
from backend.app.api.v1.endpoints.audio import router as audio_router
from backend.app.api.v1.endpoints.transcription import router as transcription_router

api_router = APIRouter()
api_router.include_router(upload_router, tags=["upload"])
api_router.include_router(audio_router, prefix="/audio", tags=["audio"])
api_router.include_router(transcription_router, tags=["transcription"])
