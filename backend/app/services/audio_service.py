import os
import time
import uuid
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import AudioExtractionError, VideoNotFoundError
from backend.app.core.logging import logger
from backend.app.models.video import Video
from backend.app.utils.ffmpeg import run_ffmpeg_extraction


class AudioService:
    @staticmethod
    def extract_audio(db: Session, video_id: str) -> dict:
        start_time = time.time()
        logger.info(f"Audio extraction started for video_id: {video_id}")

        # 1. Fetch video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(
                f"Audio extraction failed: Video database record {video_id} not found"
            )
            raise VideoNotFoundError(
                f"Video record with ID {video_id} not found"
            )

        # 2. Verify video file exists on disk
        if not os.path.exists(video.stored_path):
            logger.error(
                f"Audio extraction failed: Video file missing at {video.stored_path}"
            )
            raise VideoNotFoundError(
                f"Video file not found on disk at {video.stored_path}"
            )

        # 3. Define output path
        audio_id = str(uuid.uuid4())
        audio_filename = f"{audio_id}.wav"
        audio_path = os.path.join(settings.AUDIO_FOLDER, audio_filename)

        try:
            # 4. Perform FFmpeg extraction
            run_ffmpeg_extraction(
                video_path=video.stored_path,
                audio_path=audio_path,
                sample_rate=settings.AUDIO_SAMPLE_RATE,
                channels=settings.AUDIO_CHANNELS,
            )

            # Update video database record status if necessary, or just keep it decoupled.
            # decoupling is requested ("modular, reusable, scalable, and independent from AI transcription").
            # But we can update the status on the video record or just return.
            # Let's keep it clean and return the metadata.

            time_taken = time.time() - start_time
            logger.info(
                f"Audio extraction completed: {audio_filename} (Duration: {video.duration:.2f}s) in {time_taken:.2f}s"
            )

            return {
                "audio_id": audio_id,
                "audio_path": audio_path,
                "duration": video.duration,
                "sample_rate": settings.AUDIO_SAMPLE_RATE,
                "channels": settings.AUDIO_CHANNELS,
                "status": "completed",
            }

        except Exception as e:
            # Clean up partial output file on extraction failure
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
            logger.error(
                f"Audio extraction failed for video {video_id}: {str(e)}"
            )
            raise e
