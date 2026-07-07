import json
import os
import threading
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.rendering.asset_manager import AssetManager
from backend.app.rendering.renderer import Renderer
from backend.app.schemas.caption_style import StyleProperties
from backend.app.services.animation_service import AnimationService
from backend.app.services.caption_style_service import CaptionStyleService


class RenderService:
    # In-memory dictionary tracking rendering job state progress
    _jobs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_render_status(cls, render_id: str) -> Optional[Dict[str, Any]]:
        """
        Query rendering job progress state status.
        """
        return cls._jobs.get(render_id)

    @classmethod
    def start_render_job(
        cls,
        db: Session,
        video_id: str,
        subtitle_id: str,
        style_name: str,
        animation_preset: str,
    ) -> str:
        """
        Validates tracks registration, resolves styling and keyframes presets,
        and triggers frame compositing asynchronously in a background thread.
        """
        render_id = str(uuid.uuid4())
        cls._jobs[render_id] = {
            "render_id": render_id,
            "status": "processing",
            "progress": 0,
            "output_path": None,
            "error_message": None,
        }

        try:
            # 1. Query asset locations
            video_path = AssetManager.get_video_path(db, video_id)
            subtitles_json_path = AssetManager.get_subtitles_json_path(
                subtitle_id
            )

            # 2. Parse raw alignment segments list
            with open(subtitles_json_path, "r", encoding="utf-8") as f:
                raw_subs = json.load(f)

            # 3. Apply style layouts
            styled_data = CaptionStyleService.apply_style(
                subtitles=raw_subs,
                style_name=style_name,
                width=1080,  # Base vertical resolution width
                height=1920,
                aspect_ratio="vertical",
            )
            style_props = StyleProperties(**styled_data["style_properties"])
            styled_subs = styled_data["styled_subtitles"]

            # 4. Apply animation transitions keyframes
            animation_data = AnimationService.apply_animation(
                subtitles=styled_subs,
                style=style_props,
                preset=animation_preset,
            )
            animated_timeline = animation_data["animated_subtitles"]

            # 5. Establish output binary paths
            os.makedirs(settings.RENDERED_OUTPUT_DIR, exist_ok=True)
            output_filename = f"rendered_{render_id}.mp4"
            output_path = os.path.join(
                settings.RENDERED_OUTPUT_DIR, output_filename
            )

            # 6. Trigger thread processing loop
            thread = threading.Thread(
                target=cls._run_render_task,
                args=(
                    render_id,
                    video_path,
                    animated_timeline,
                    style_props,
                    output_path,
                ),
                daemon=True,
            )
            thread.start()

            return render_id

        except Exception as e:
            logger.error(f"Render job init failure: {str(e)}")
            cls._jobs[render_id]["status"] = "failed"
            cls._jobs[render_id]["error_message"] = str(e)
            return render_id

    @classmethod
    def _run_render_task(
        cls,
        render_id: str,
        video_path: str,
        animated_timeline: List[Dict[str, Any]],
        style_props: StyleProperties,
        output_path: str,
    ) -> None:
        logger.info(
            f"Background thread starting frame composition loop for job ID: {render_id}"
        )

        def progress_callback(progress: int):
            cls._jobs[render_id]["progress"] = progress
            if progress < 100:
                cls._jobs[render_id]["status"] = "rendering"

        try:
            Renderer.render(
                video_path=video_path,
                animation_timeline=animated_timeline,
                style=style_props,
                output_path=output_path,
                progress_callback=progress_callback,
            )
            cls._jobs[render_id]["output_path"] = output_path
            cls._jobs[render_id]["progress"] = 100
            cls._jobs[render_id]["status"] = "completed"
            logger.info(
                f"Background frame compositor successfully finished for job ID: {render_id}"
            )
        except Exception as e:
            logger.error(
                f"Background frame compositor failed for job ID {render_id}: {str(e)}"
            )
            cls._jobs[render_id]["status"] = "failed"
            cls._jobs[render_id]["error_message"] = str(e)
