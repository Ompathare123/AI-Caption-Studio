import subprocess
from backend.app.core.config import settings
from backend.app.core.errors import AudioExtractionError, FFmpegNotFoundError
from backend.app.core.logging import logger


def is_ffmpeg_installed() -> bool:
    """
    Check if the configured FFMPEG_PATH executable is available and callable.
    """
    try:
        subprocess.run(
            [settings.FFMPEG_PATH, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_ffmpeg_extraction(
    video_path: str,
    audio_path: str,
    sample_rate: int = 16000,
    channels: int = 1,
    timeout: int = 60,
) -> None:
    """
    Invoke FFmpeg subprocess to extract audio in PCM 16-bit Mono WAV format.
    """
    if not is_ffmpeg_installed():
        logger.error(
            f"FFmpeg executable not found at path: {settings.FFMPEG_PATH}"
        )
        raise FFmpegNotFoundError()

    cmd = [
        settings.FFMPEG_PATH,
        "-y",  # Overwrite existing files without asking
        "-i",
        video_path,  # Input video file path
        "-vn",  # Disable video recording/extraction
        "-acodec",
        "pcm_s16le",  # WAV 16-bit PCM codec
        "-ar",
        str(sample_rate),  # Resample rate (e.g., 16000 Hz)
        "-ac",
        str(channels),  # Set channel count (e.g., 1 for mono)
        audio_path,  # Output audio file path
    ]

    logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error(
                f"FFmpeg process failed with exit code {result.returncode}. Stderr: {result.stderr}"
            )
            if "Output file does not contain any stream" in result.stderr:
                raise AudioExtractionError(
                    "The input video file does not contain any audio track."
                )
            raise AudioExtractionError(
                f"FFmpeg extraction failed: {result.stderr.splitlines()[-1] if result.stderr else 'Unknown error'}"
            )
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg extraction timed out after {timeout} seconds")
        raise AudioExtractionError("Audio extraction operation timed out.")
    except Exception as e:
        logger.error(f"Failed to run FFmpeg: {str(e)}")
        if not isinstance(e, AudioExtractionError):
            raise AudioExtractionError(
                f"Internal subprocess failure: {str(e)}"
            )
        raise e
