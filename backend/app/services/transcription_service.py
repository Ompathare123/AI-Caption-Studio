import os
import time
import uuid
from typing import Optional
from faster_whisper import WhisperModel

from backend.app.core.config import settings
from backend.app.core.errors import AudioNotFoundError, TranscriptionError
from backend.app.core.logging import logger


class TranscriptionService:
    # Singleton model instance cached in class memory
    _model: Optional[WhisperModel] = None

    @classmethod
    def load_model(cls) -> None:
        """
        Load the Faster-Whisper model into memory. Reuses instance if already loaded.
        """
        if cls._model is not None:
            return

        logger.info(
            f"Loading Faster-Whisper model '{settings.WHISPER_MODEL}' "
            f"on device '{settings.DEVICE}' ({settings.COMPUTE_TYPE})..."
        )
        try:
            start_time = time.time()
            cls._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.DEVICE,
                compute_type=settings.COMPUTE_TYPE,
            )
            duration = time.time() - start_time
            logger.info(
                f"Model '{settings.WHISPER_MODEL}' Loaded successfully in {duration:.2f}s"
            )
        except Exception as e:
            logger.error(f"Failed to load Faster-Whisper model: {str(e)}")
            raise TranscriptionError(f"Model loading failure: {str(e)}")

    @classmethod
    def get_model(cls) -> WhisperModel:
        """
        Access the loaded model instance. Loads it if not initialized.
        """
        if cls._model is None:
            cls.load_model()
        return cls._model

    @classmethod
    def transcribe_audio(cls, audio_id: str) -> dict:
        """
        Validate audio existence and execute speech-to-text transcription.
        """
        audio_filename = f"{audio_id}.wav"
        audio_path = os.path.join(settings.AUDIO_FOLDER, audio_filename)

        # 1. Validate file exists
        if not os.path.exists(audio_path):
            logger.error(
                f"Transcription failed: Audio file missing at {audio_path}"
            )
            raise AudioNotFoundError(
                f"Audio file with ID {audio_id} not found on disk"
            )

        # 2. Acquire model
        model = cls.get_model()

        logger.info(f"Transcription Started for audio_id: {audio_id}")
        start_time = time.time()

        try:
            # 3. Execute transcription
            segments, info = model.transcribe(audio_path, beam_size=5)

            logger.info(
                f"Language Detected: {info.language} "
                f"(probability: {info.language_probability:.2f})"
            )
            logger.info(f"Audio Duration: {info.duration:.2f}s")

            # Iterate the segments generator to trigger computation
            formatted_segments = []
            for segment in segments:
                formatted_segments.append(
                    {
                        "start": round(segment.start, 2),
                        "end": round(segment.end, 2),
                        "text": segment.text.strip(),
                    }
                )

            processing_time = time.time() - start_time
            logger.info(
                f"Transcription Finished: {audio_filename} in {processing_time:.2f}s"
            )

            return {
                "id": str(uuid.uuid4()),
                "language": info.language,
                "duration": round(info.duration, 2),
                "processing_time": round(processing_time, 2),
                "segments": formatted_segments,
                "status": "completed",
            }

        except Exception as e:
            logger.error(
                f"Transcription failed for audio {audio_id}: {str(e)}"
            )
            raise TranscriptionError(
                f"Internal transcription execution failed: {str(e)}"
            )
