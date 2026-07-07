from typing import Any, Dict, List

from backend.app.animations.animation_manager import AnimationManager
from backend.app.animations.timeline_generator import TimelineGenerator
from backend.app.core.logging import logger
from backend.app.schemas.caption_style import StyleProperties


class AnimationService:

    @staticmethod
    def list_animations() -> List[str]:
        """
        Return names of all supported animation preset profiles.
        """
        return [
            "word_highlight",
            "word_pop",
            "word_scale",
            "word_fade",
            "word_bounce",
            "word_slide",
            "word_rotate",
            "word_blur",
            "letter_animation",
            "character_animation",
            "sentence_fade",
            "sentence_pop",
            "karaoke_highlight",
            "progress_fill",
            "opacity_fade",
            "zoom_in",
            "zoom_out",
        ]

    @staticmethod
    def apply_animation(
        subtitles: List[Dict[str, Any]], style: StyleProperties, preset: str
    ) -> Dict[str, Any]:
        """
        Orchestrate total duration compilation, preset validation, and timeline caching.
        """
        preset_clean = preset.lower().strip()
        available = AnimationService.list_animations()

        if preset_clean not in [p.lower() for p in available]:
            logger.warning(
                f"Unknown animation preset '{preset}' requested - falling back to 'word_highlight'"
            )
            preset_clean = "word_highlight"

        total_duration = TimelineGenerator.calculate_total_duration(subtitles)

        # Retrieve or compute keyframe mapping from cache
        animated_subs = AnimationManager.get_animated_timeline(
            subtitles=subtitles, style=style, preset=preset_clean
        )

        return {
            "animation_preset": preset_clean,
            "duration": round(total_duration, 2),
            "animated_subtitles": animated_subs,
        }
