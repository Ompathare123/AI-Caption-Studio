from typing import Any, Dict, List

from backend.app.core.logging import logger
from backend.app.services.style_loader import StyleLoader
from backend.app.services.style_manager import StyleManager


class CaptionStyleService:

    @staticmethod
    def list_styles() -> List[str]:
        """
        List all default and custom styles.
        """
        return StyleLoader.list_styles()

    @staticmethod
    def create_custom_style(style_name: str, style_data: Dict[str, Any]) -> str:
        """
        Create and save a new custom style config file.
        """
        return StyleLoader.save_custom_style(style_name, style_data)

    @staticmethod
    def apply_style(
        subtitles: List[Dict[str, Any]],
        style_name: str,
        width: int,
        height: int,
        aspect_ratio: str,
    ) -> Dict[str, Any]:
        """
        Orchestrates style loading, resolution scaling, and text rendering effects.
        """
        logger.info(
            f"Applying style '{style_name}' to {len(subtitles)} segments "
            f"for video frame resolution {width}x{height} ({aspect_ratio})..."
        )

        # 1. Load style definition
        style_data = StyleLoader.load_style(style_name)

        # 2. Scale style properties responsively
        scaled_properties = StyleManager.scale_style(
            style_data=style_data, width=width, aspect_ratio=aspect_ratio
        )

        # 3. Apply text styling and casings to word lists
        styled_segments = []
        effects = style_data.get("text_effects", {})

        for seg in subtitles:
            styled_seg = StyleManager.apply_text_effects(seg, effects)
            styled_segments.append(styled_seg)

        logger.info(
            f"Style '{style_name}' applied successfully. Resulting font size: "
            f"{scaled_properties.get('font_size')}"
        )

        return {
            "style_name": style_name,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "style_properties": scaled_properties,
            "styled_subtitles": styled_segments,
        }
