import hashlib
import os
from datetime import datetime
from backend.app.core.config import settings

# Allowed MIME types for supported video extensions
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",  # .mov
    "video/x-msvideo",  # .avi
    "video/avi",
    "video/msvideo",
    "video/x-matroska",  # .mkv
    "video/mkv",
    "video/webm",
}


def is_allowed_extension(filename: str) -> bool:
    """
    Check if the file extension is allowed.
    """
    _, ext = os.path.splitext(filename.lower())
    return ext in settings.ALLOWED_EXTENSIONS


def is_allowed_mime_type(content_type: str) -> bool:
    """
    Check if the MIME type is allowed.
    """
    return content_type.lower() in ALLOWED_MIME_TYPES


def get_dynamic_upload_path(filename: str, file_id: str) -> str:
    """
    Generate a dynamic date-based destination path.
    Example: backend/uploads/2026/07/video_uuid.mp4
    """
    _, ext = os.path.splitext(filename.lower())
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # Construct directory path
    relative_dir = os.path.join(year, month)
    target_dir = os.path.join(settings.UPLOAD_DIR, relative_dir)

    # Ensure directories exist
    os.makedirs(target_dir, exist_ok=True)

    return os.path.join(target_dir, f"{file_id}{ext}")


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file in chunks to optimize memory.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 64kb chunks
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
