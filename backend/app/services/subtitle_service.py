import json
import time
import uuid
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import AlignmentError, AlignmentNotFoundError
from backend.app.core.logging import logger
from backend.app.models.alignment import Alignment
from backend.app.services.subtitle_builder import SubtitleBuilder
from backend.app.services.subtitle_exporter import SubtitleExporter
from backend.app.services.subtitle_formatter import SubtitleFormatter


class SubtitleService:

    @staticmethod
    def generate_subtitles(
        db: Session,
        alignment_id: str,
        style: str = "default",
        max_words_per_line: int = 5,
        max_lines: int = 2,
        output_formats: list = None,
    ) -> dict:
        """
        Orchestrates fetching alignment data, caption segmentation, formatting,
        and exporting to JSON, SRT, and ASS files.
        """
        if output_formats is None:
            output_formats = ["json", "srt", "ass"]

        start_time = time.time()
        logger.info(
            f"Subtitle Generation Started for alignment_id: {alignment_id}"
        )

        # 1. Fetch alignment record from database
        alignment = (
            db.query(Alignment).filter(Alignment.id == alignment_id).first()
        )
        if not alignment:
            logger.error(
                f"Subtitle Generation failed: Alignment record {alignment_id} not found"
            )
            raise AlignmentNotFoundError(
                f"Alignment record with ID {alignment_id} not found"
            )

        try:
            # 2. Deserialize words list
            words = json.loads(alignment.words_json)
            if not words:
                raise AlignmentError("Alignment record has no words data to segment.")

            # 3. Segment words into captions
            captions = SubtitleBuilder.build_captions(
                words=words,
                max_words_per_line=max_words_per_line,
                max_lines=max_lines,
                reading_speed=settings.READING_SPEED,
            )

            # 4. Generate and export formats
            subtitle_files = {}
            generated_formats_list = []

            for fmt in output_formats:
                fmt_lower = fmt.lower().strip()
                filename = f"{alignment_id}.{fmt_lower}"

                if fmt_lower == "json":
                    content = SubtitleFormatter.to_json(captions)
                    filepath = SubtitleExporter.export_subtitle(
                        content, filename
                    )
                    subtitle_files["json"] = filepath
                    generated_formats_list.append("JSON")

                elif fmt_lower == "srt":
                    content = SubtitleFormatter.to_srt(captions)
                    filepath = SubtitleExporter.export_subtitle(
                        content, filename
                    )
                    subtitle_files["srt"] = filepath
                    generated_formats_list.append("SRT")

                elif fmt_lower == "ass":
                    content = SubtitleFormatter.to_ass(captions, style=style)
                    filepath = SubtitleExporter.export_subtitle(
                        content, filename
                    )
                    subtitle_files["ass"] = filepath
                    generated_formats_list.append("ASS")

            processing_time = time.time() - start_time
            logger.info(
                f"Subtitle Generation Finished: generated {len(captions)} captions "
                f"in formats {', '.join(generated_formats_list)} in {processing_time:.2f}s"
            )

            return {
                "id": str(uuid.uuid4()),
                "subtitle_files": subtitle_files,
                "caption_count": len(captions),
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Subtitle Generation execution failed: {str(e)}")
            if isinstance(e, (AlignmentNotFoundError, AlignmentError)):
                raise e
            raise AlignmentError(
                f"Internal subtitle generation failure: {str(e)}"
            )
