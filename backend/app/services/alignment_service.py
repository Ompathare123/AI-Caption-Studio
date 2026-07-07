import json
import os
import time
from typing import Any, Dict, Tuple
import whisperx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import (
    AlignmentError,
    AudioNotFoundError,
    TranscriptNotFoundError,
)
from backend.app.core.logging import logger
from backend.app.models.alignment import Alignment
from backend.app.models.transcript import Transcript


class AlignmentService:
    # Cache to store loaded align models per language: { "en": (model, metadata) }
    _align_models: Dict[str, Tuple[Any, Any]] = {}

    @classmethod
    def get_align_model(cls, language_code: str) -> Tuple[Any, Any]:
        """
        Load and cache the WhisperX alignment model for the given language.
        """
        if language_code in cls._align_models:
            return cls._align_models[language_code]

        logger.info(
            f"Loading WhisperX alignment model for language '{language_code}' "
            f"on device '{settings.ALIGNMENT_DEVICE}'..."
        )
        try:
            start_time = time.time()
            model_a, metadata = whisperx.load_align_model(
                language_code=language_code,
                device=settings.ALIGNMENT_DEVICE,
            )
            cls._align_models[language_code] = (model_a, metadata)
            duration = time.time() - start_time
            logger.info(
                f"WhisperX alignment model '{language_code}' loaded in {duration:.2f}s"
            )
            return model_a, metadata
        except Exception as e:
            logger.error(
                f"Failed to load WhisperX alignment model for '{language_code}': {str(e)}"
            )
            raise AlignmentError(
                f"Alignment model loading failure for language '{language_code}': {str(e)}"
            )

    @classmethod
    def align_transcript(
        cls, db: Session, audio_id: str, transcript_id: str
    ) -> dict:
        """
        Fetch transcript segments and run phonetic wave alignment using WhisperX.
        Saves result to alignments database table.
        """
        start_time = time.time()
        logger.info(
            f"Alignment Started: audio_id={audio_id}, transcript_id={transcript_id}"
        )

        # 1. Fetch transcript from database
        transcript = (
            db.query(Transcript).filter(Transcript.id == transcript_id).first()
        )
        if not transcript:
            logger.error(
                f"Alignment failed: Transcript record {transcript_id} not found"
            )
            raise TranscriptNotFoundError(
                f"Transcript record with ID {transcript_id} not found"
            )

        # 2. Check if audio file exists on disk
        audio_filename = f"{audio_id}.wav"
        audio_path = os.path.join(settings.AUDIO_FOLDER, audio_filename)
        if not os.path.exists(audio_path):
            logger.error(
                f"Alignment failed: Audio file missing at {audio_path}"
            )
            raise AudioNotFoundError(
                f"Audio file with ID {audio_id} not found on disk"
            )

        try:
            # 3. Load audio file using WhisperX
            audio = whisperx.load_audio(audio_path)
            # Duration in seconds (sample count / sample rate)
            duration = (
                len(audio) / whisperx.audio.SAMPLE_RATE
                if whisperx.audio.SAMPLE_RATE > 0
                else 0.0
            )

            # 4. Format segments from database
            segments = []
            for seg in transcript.segments:
                segments.append(
                    {"start": seg.start, "end": seg.end, "text": seg.text}
                )

            if not segments:
                raise AlignmentError(
                    "The transcript contains no text segments to align."
                )

            # 5. Retrieve alignment model
            model_a, metadata = cls.get_align_model(transcript.language)

            # 6. Execute alignment
            logger.info(f"Aligning {len(segments)} segments...")
            result = whisperx.align(
                segments,
                model_a,
                metadata,
                audio,
                settings.ALIGNMENT_DEVICE,
                return_char_alignments=False,
            )

            # 7. Parse words from aligned segments
            aligned_words = []
            for seg in result.get("segments", []):
                for word_info in seg.get("words", []):
                    # Score represents confidence in WhisperX
                    aligned_words.append(
                        {
                            "word": word_info.get("word"),
                            "start": word_info.get("start"),
                            "end": word_info.get("end"),
                            "confidence": word_info.get("score"),
                        }
                    )

            # 8. Save alignment results to database
            db_alignment = Alignment(
                transcript_id=transcript_id,
                audio_id=audio_id,
                language=transcript.language,
                duration=round(duration, 2),
                status="completed",
                words_json=json.dumps(aligned_words),
            )
            db.add(db_alignment)
            db.commit()
            db.refresh(db_alignment)

            processing_time = time.time() - start_time
            logger.info(
                f"Alignment Finished: {audio_filename} "
                f"(Aligned {len(aligned_words)} words) in {processing_time:.2f}s"
            )

            return {
                "id": db_alignment.id,
                "language": db_alignment.language,
                "duration": db_alignment.duration,
                "words": aligned_words,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Alignment execution failed: {str(e)}")
            if isinstance(
                e, (AudioNotFoundError, TranscriptNotFoundError, AlignmentError)
            ):
                raise e
            raise AlignmentError(f"Internal alignment execution failed: {str(e)}")
