import subprocess
from backend.app.core.config import settings
from backend.app.core.errors import RenderingError
from backend.app.core.logging import logger


class VideoEncoder:

    @staticmethod
    def merge_audio(
        rendered_v_path: str, original_v_path: str, output_path: str
    ) -> None:
        """
        Merges the captioned video stream with the original audio track using FFmpeg.
        Uses optional mapping to prevent failures for audio-less videos.
        """
        cmd = [
            settings.FFMPEG_PATH,
            "-y",
            "-i",
            rendered_v_path,
            "-i",
            original_v_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0?",  # ? handles video-only tracks without throwing errors
            "-shortest",  # aligns tracks boundary ends
            output_path,
        ]

        logger.info(f"VideoEncoder running FFmpeg: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            logger.info("FFmpeg audio re-muxing completed successfully.")
        except subprocess.CalledProcessError as cpe:
            logger.error(f"FFmpeg command execution failed: {cpe.stderr}")
            raise RenderingError(
                f"FFmpeg audio merge failed: {cpe.stderr or cpe.stdout}"
            )
        except Exception as e:
            logger.error(f"Encoder process error: {str(e)}")
            raise RenderingError(f"Encoder pipeline fail: {str(e)}")
