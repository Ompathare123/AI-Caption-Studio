import os

from backend.app.core.config import settings
from backend.app.core.errors import VideoUploadError


class SubtitleExportError(VideoUploadError):

    def __init__(self, message: str = "Failed to export subtitle files"):
        super().__init__(message, status_code=500)


class SubtitleExporter:

    @staticmethod
    def export_subtitle(content: str, filename: str) -> str:
        """
        Saves subtitle content to the output directory using UTF-8 encoding.
        Protects against directory structure creation, disk full, and permission errors.
        """
        output_dir = settings.SUBTITLES_OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return filepath
        except PermissionError as pe:
            raise SubtitleExportError(
                f"Permission denied writing subtitle file to disk at {filepath}: {str(pe)}"
            )
        except OSError as oe:
            # Handles disk full (ENOSPC) or general OS file system blocks
            raise SubtitleExportError(
                f"Disk or system write error writing subtitle file at {filepath}: {str(oe)}"
            )
        except Exception as e:
            raise SubtitleExportError(
                f"Unexpected write execution failure: {str(e)}"
            )
