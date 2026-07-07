from typing import Any, Callable, Dict, List, Optional

from backend.app.rendering.video_renderer import VideoRenderer
from backend.app.schemas.caption_style import StyleProperties


class Renderer:

    @staticmethod
    def render(
        video_path: str,
        animation_timeline: List[Dict[str, Any]],
        style: StyleProperties,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> str:
        """
        High-level wrapper interfacing client modules with the video frame loops.
        """
        return VideoRenderer.render_captioned_video(
            video_path=video_path,
            animation_timeline=animation_timeline,
            style=style,
            output_path=output_path,
            progress_callback=progress_callback,
        )
