from typing import Any, Dict

import cv2
import numpy as np
from PIL import Image, ImageDraw

from backend.app.rendering.font_manager import FontManager
from backend.app.rendering.subtitle_renderer import SubtitleRenderer
from backend.app.rendering.timeline_player import TimelinePlayer
from backend.app.schemas.caption_style import StyleProperties


class FrameRenderer:

    @staticmethod
    def render_frame(
        frame: np.ndarray,
        t: float,
        active_segment: Dict[str, Any],
        style: StyleProperties,
    ) -> np.ndarray:
        """
        Renders styled animated captions on top of a single video frame.
        Handles opacity blend layers, rounded boxes, borders, shadows, and rotation angles.
        """
        if not active_segment:
            return frame

        h, w, _ = frame.shape

        # 1. Convert OpenCV frame to PIL RGBA Image
        pil_frame = Image.fromarray(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ).convert("RGBA")
        text_layer = Image.new("RGBA", pil_frame.size, (0, 0, 0, 0))

        # 2. Retrieve positioned word layout coordinates
        positioned_words = SubtitleRenderer.layout_segment(
            active_segment, style, w, h
        )

        for p_word in positioned_words:
            word_info = p_word["word_info"]

            # Evaluate animated properties at timestamp t
            state = TimelinePlayer.get_word_properties_at_time(word_info, t)

            word_text = p_word["word"]

            scale = state.get("scale", 1.0)
            opacity = state.get("opacity", 1.0)
            rotation = state.get("rotation", 0.0)
            pos_x = state.get("position_x", 0.0)
            pos_y = state.get("position_y", 0.0)
            color = state.get("color", style.text_color)

            # Resolve scaled dynamic font size
            font_size = max(1, int(round(style.font_size * scale)))
            font = FontManager.load_truetype_font(style.font_family, font_size)

            def hex_to_rgba(hex_str: str, alpha: float = 1.0) -> tuple:
                try:
                    hex_str = hex_str.lstrip("#")
                    r, g, b = (
                        int(hex_str[0:2], 16),
                        int(hex_str[2:4], 16),
                        int(hex_str[4:6], 16),
                    )
                    return (r, g, b, int(alpha * 255))
                except Exception:
                    return (255, 255, 255, int(alpha * 255))

            text_color_rgba = hex_to_rgba(color, opacity)

            # Compute word dimensions bounding box
            dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            word_bbox = dummy_draw.textbbox((0, 0), word_text, font=font)
            word_w = word_bbox[2] - word_bbox[0]
            word_h = word_bbox[3] - word_bbox[1]

            # Create a small temp canvas layer with margins to avoid clipping during rotation
            padding = int(style.padding) + 15
            temp_w = word_w + padding * 2
            temp_h = word_h + padding * 2

            word_img = Image.new("RGBA", (temp_w, temp_h), (0, 0, 0, 0))
            word_draw = ImageDraw.Draw(word_img)

            # Centering offset bounds
            draw_x = padding - word_bbox[0]
            draw_y = padding - word_bbox[1]

            # 3. Draw Background Box (scales with word elements)
            if style.background_box:
                box_color = hex_to_rgba(
                    style.background_color, style.background_opacity * opacity
                )
                box_x0 = draw_x + word_bbox[0] - style.padding
                box_y0 = draw_y + word_bbox[1] - style.padding
                box_x1 = draw_x + word_bbox[2] + style.padding
                box_y1 = draw_y + word_bbox[3] + style.padding

                word_draw.rounded_rectangle(
                    [box_x0, box_y0, box_x1, box_y1],
                    radius=style.border_radius,
                    fill=box_color,
                )

            # 4. Draw Shadows
            if style.shadow_offset_x or style.shadow_offset_y:
                shadow_col = hex_to_rgba(style.shadow_color or "#000000", opacity)
                shadow_x = draw_x + style.shadow_offset_x
                shadow_y = draw_y + style.shadow_offset_y
                word_draw.text(
                    (shadow_x, shadow_y), word_text, fill=shadow_col, font=font
                )

            # 5. Draw main text with Outline borders
            outline_w = int(style.outline_width)
            outline_col = (
                hex_to_rgba(style.outline_color, opacity)
                if outline_w > 0
                else None
            )

            word_draw.text(
                (draw_x, draw_y),
                word_text,
                fill=text_color_rgba,
                font=font,
                stroke_width=outline_w,
                stroke_fill=outline_col,
            )

            # 6. Apply Rotation angles
            if rotation != 0.0:
                rotated_word_img = word_img.rotate(
                    rotation, resample=Image.Resample.BICUBIC, expand=True
                )
            else:
                rotated_word_img = word_img

            # 7. Calculate paste anchor coordinates and compositing mask
            paste_x = int(
                p_word["x"] - (rotated_word_img.width - word_w) / 2.0 + pos_x
            )
            paste_y = int(
                p_word["y"] - (rotated_word_img.height - word_h) / 2.0 + pos_y
            )

            text_layer.paste(
                rotated_word_img, (paste_x, paste_y), rotated_word_img
            )

        # 8. Composite text overlay layer onto frame
        composite = Image.alpha_composite(pil_frame, text_layer)

        # 9. Convert back to OpenCV BGR frame
        return cv2.cvtColor(np.array(composite), cv2.COLOR_RGBA2BGR)
