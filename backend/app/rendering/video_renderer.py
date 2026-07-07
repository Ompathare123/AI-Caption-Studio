import os
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
import cv2

from backend.app.core.config import settings
from backend.app.core.errors import RenderingError
from backend.app.core.logging import logger
from backend.app.rendering.frame_renderer import FrameRenderer
from backend.app.rendering.timeline_player import TimelinePlayer
from backend.app.rendering.video_encoder import VideoEncoder
from backend.app.schemas.caption_style import StyleProperties


class VideoRenderer:

    @staticmethod
    def render_captioned_video(
        video_path: str,
        animation_timeline: List[Dict[str, Any]],
        style: StyleProperties,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> str:
        """
        Decouples frame iteration from encoding. Extracts video frames using OpenCV,
        applies Pillow style draws, and runs FFmpeg audio re-muxing.
        """
        logger.info(f"VideoRenderer frame loop started for: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RenderingError(
                f"Failed to open source video reader at path: {video_path}"
            )

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps <= 0 or total_frames <= 0:
            fps = 30.0
            total_frames = 1

        # Create temporary video file path
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        temp_rendered_path = os.path.join(
            settings.TEMP_DIR, f"temp_render_{uuid.uuid4()}.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            temp_rendered_path, fourcc, fps, (width, height)
        )

        start_time = time.time()
        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                t = frame_idx / fps

                # Query timeline player for active captions segment at time t
                active_seg = TimelinePlayer.get_active_segment(
                    animation_timeline, t
                )

                # Render caption overlay on frame
                rendered_frame = FrameRenderer.render_frame(
                    frame=frame, t=t, active_segment=active_seg, style=style
                )

                writer.write(rendered_frame)

                frame_idx += 1

                if progress_callback:
                    # Allocate 90% of progress to frame drawing, leaving 10% for audio merge
                    pct = int((frame_idx / total_frames) * 90)
                    progress_callback(min(90, pct))

            logger.info(
                f"Frame rendering loop completed. Processed {frame_idx} frames."
            )
        except Exception as e:
            logger.error(f"Error during video frame loop iteration: {str(e)}")
            raise RenderingError(
                f"Video frame rendering failed: {str(e)}"
            )
        finally:
            cap.release()
            writer.release()

        # Merge original audio track back with rendered video
        if progress_callback:
            progress_callback(95)

        try:
            VideoEncoder.merge_audio(
                rendered_v_path=temp_rendered_path,
                original_v_path=video_path,
                output_path=output_path,
            )
            if progress_callback:
                progress_callback(100)
        finally:
            if os.path.exists(temp_rendered_path):
                try:
                    os.remove(temp_rendered_path)
                except Exception:
                    pass

        elapsed = time.time() - start_time
        fps_render = frame_idx / elapsed if elapsed > 0 else 0.0
        logger.info(
            f"Video Caption Render Finished in {elapsed:.2f}s (Average FPS: {fps_render:.2f})"
        )

        return output_path
