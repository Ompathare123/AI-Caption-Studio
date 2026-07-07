import os
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import RenderingError
from backend.app.models.video import Video


class AssetManager:

    @staticmethod
    def get_video_path(db: Session, video_id: str) -> str:
        """
        Retrieves the absolute path of the source video from DB metadata
        and asserts file existence.
        """
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise RenderingError(
                f"Video record '{video_id}' not registered in database",
                status_code=404,
            )

        stored_path = video.stored_path
        if not os.path.exists(stored_path):
            raise RenderingError(
                f"Video binary for ID '{video_id}' missing from storage location: {stored_path}",
                status_code=404,
            )

        return stored_path

    @staticmethod
    def get_subtitles_json_path(subtitle_id: str) -> str:
        """
        Locates the compiled Subtitle JSON file on disk, supporting direct matches
        and wildcard folder scans.
        """
        sub_clean = subtitle_id.strip()

        # 1. Direct alignment/task ID mapping
        json_path = os.path.join(
            settings.SUBTITLES_OUTPUT_DIR, f"{sub_clean}.json"
        )
        if os.path.exists(json_path):
            return json_path

        # 2. Scanning folder fallback
        if os.path.exists(settings.SUBTITLES_OUTPUT_DIR):
            for file in os.listdir(settings.SUBTITLES_OUTPUT_DIR):
                if file.endswith(".json") and sub_clean in file:
                    return os.path.join(settings.SUBTITLES_OUTPUT_DIR, file)

        raise RenderingError(
            f"Subtitle alignment file matching '{subtitle_id}' not found on disk",
            status_code=404,
        )
