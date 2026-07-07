from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.app.core.logging import logger


class VideoUploadError(Exception):
    """Base exception for all video upload errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidExtensionError(VideoUploadError):
    def __init__(self, message: str = "Invalid file extension"):
        super().__init__(message, status_code=400)


class InvalidMIMETypeError(VideoUploadError):
    def __init__(self, message: str = "Invalid MIME type"):
        super().__init__(message, status_code=400)


class FileTooLargeError(VideoUploadError):
    def __init__(self, message: str = "File size exceeds the limit"):
        super().__init__(message, status_code=413)


class CorruptedVideoError(VideoUploadError):
    def __init__(self, message: str = "Corrupted or unreadable video file"):
        super().__init__(message, status_code=400)


class DuplicateVideoError(VideoUploadError):
    def __init__(self, message: str = "Video file has already been uploaded"):
        super().__init__(message, status_code=409)


class VideoNotFoundError(VideoUploadError):
    def __init__(self, message: str = "Video not found"):
        super().__init__(message, status_code=404)


class FFmpegNotFoundError(VideoUploadError):
    def __init__(self, message: str = "FFmpeg installation is not available on this server"):
        super().__init__(message, status_code=500)


class AudioExtractionError(VideoUploadError):
    def __init__(self, message: str = "Failed to extract audio from video"):
        super().__init__(message, status_code=500)


class AudioNotFoundError(VideoUploadError):
    def __init__(self, message: str = "Audio file not found"):
        super().__init__(message, status_code=404)


class TranscriptionError(VideoUploadError):
    def __init__(self, message: str = "Transcription failed"):
        super().__init__(message, status_code=500)


class TranscriptNotFoundError(VideoUploadError):
    def __init__(self, message: str = "Transcript record not found"):
        super().__init__(message, status_code=404)


class AlignmentNotFoundError(VideoUploadError):
    def __init__(self, message: str = "Alignment record not found"):
        super().__init__(message, status_code=404)


class AlignmentError(VideoUploadError):
    def __init__(self, message: str = "Audio alignment failed"):
        super().__init__(message, status_code=500)


class StyleNotFoundError(VideoUploadError):
    def __init__(self, message: str = "Style definition not found"):
        super().__init__(message, status_code=404)


class StyleValidationError(VideoUploadError):
    def __init__(self, message: str = "Invalid style properties"):
        super().__init__(message, status_code=400)


class RenderingError(VideoUploadError):
    def __init__(self, message: str = "Video rendering failed", status_code: int = 500):
        super().__init__(message, status_code=status_code)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(VideoUploadError)
    async def video_upload_error_handler(request: Request, exc: VideoUploadError):
        logger.error(f"Upload validation failed: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("An unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."}
        )
