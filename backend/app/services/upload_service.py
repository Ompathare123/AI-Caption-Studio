import os
import shutil
import time
import uuid
import cv2
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import (
    CorruptedVideoError,
    DuplicateVideoError,
    FileTooLargeError,
    InvalidExtensionError,
    InvalidMIMETypeError,
    VideoUploadError,
)
from backend.app.core.logging import logger
from backend.app.models.video import Video
from backend.app.utils.file_utils import (
    calculate_file_hash,
    get_dynamic_upload_path,
    is_allowed_extension,
    is_allowed_mime_type,
)


class UploadService:
    @staticmethod
    async def process_upload(db: Session, file: UploadFile) -> Video:
        start_time = time.time()
        logger.info(f"Upload started for file: {file.filename}")

        if not file.filename:
            logger.error("Upload failed: Missing filename")
            raise VideoUploadError("Missing file name")

        # 1. Validate extension and MIME type
        if not is_allowed_extension(file.filename):
            logger.error(f"Upload failed: Invalid extension for {file.filename}")
            raise InvalidExtensionError(
                f"Extension not allowed. Supported: {settings.ALLOWED_EXTENSIONS}"
            )

        if not file.content_type or not is_allowed_mime_type(file.content_type):
            logger.error(
                f"Upload failed: Invalid MIME type {file.content_type} for {file.filename}"
            )
            raise InvalidMIMETypeError(
                "MIME type not allowed. Please upload a valid video file."
            )

        # 2. Write to a temporary file in chunks to limit memory usage
        file_id = str(uuid.uuid4())
        _, ext = os.path.splitext(file.filename.lower())
        temp_filename = f"temp_{file_id}{ext}"
        temp_path = os.path.join(settings.TEMP_DIR, temp_filename)

        total_size = 0
        try:
            with open(temp_path, "wb") as temp_file:
                # Read file in 1MB chunks
                while chunk := await file.read(1024 * 1024):
                    total_size += len(chunk)
                    if total_size > settings.MAX_UPLOAD_SIZE:
                        raise FileTooLargeError(
                            f"File size exceeds the maximum limit of "
                            f"{settings.MAX_UPLOAD_SIZE / (1024**3):.1f} GB"
                        )
                    temp_file.write(chunk)

            if total_size == 0:
                raise VideoUploadError("Empty upload file")

            # 3. Compute SHA-256 Hash and check for duplicates
            file_hash = calculate_file_hash(temp_path)
            duplicate = (
                db.query(Video).filter(Video.file_hash == file_hash).first()
            )
            if duplicate:
                raise DuplicateVideoError(
                    f"Duplicate upload. This video has already been uploaded with ID: {duplicate.id}"
                )

            # 4. Verify integrity and extract duration with OpenCV
            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                raise CorruptedVideoError("Corrupted or unreadable video file")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()

            if fps <= 0 or frame_count <= 0:
                raise CorruptedVideoError(
                    "Invalid video properties. The file may be corrupted."
                )

            duration = frame_count / fps

            # 5. Determine final dynamic path and move file
            final_path = get_dynamic_upload_path(file.filename, file_id)
            shutil.move(temp_path, final_path)

            # 6. Save metadata to database
            db_video = Video(
                id=file_id,
                filename=file.filename,
                stored_path=final_path,
                file_hash=file_hash,
                size=total_size,
                duration=duration,
                status="uploaded",
            )
            db.add(db_video)
            db.commit()
            db.refresh(db_video)

            processing_time = time.time() - start_time
            logger.info(
                f"Upload completed: {file.filename} (ID: {file_id}) in {processing_time:.2f}s"
            )

            return db_video

        except Exception as e:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Upload failed: {file.filename} - {str(e)}")
            raise e
