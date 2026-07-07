from typing import Any, Dict, List
from PIL import Image, ImageDraw

from backend.app.rendering.font_manager import FontManager
from backend.app.schemas.caption_style import StyleProperties


class SubtitleRenderer:

    @staticmethod
    def layout_segment(
        segment: Dict[str, Any],
        style: StyleProperties,
        width: int,
        height: int,
    ) -> List[Dict[str, Any]]:
        """
        Computes the absolute layout coordinates (X, Y) of each word in a segment
        handling safe margins, spacings, alignment anchors, and line indexes.
        """
        words = segment.get("words", [])
        if not words:
            return []

        # 1. Group words by line index metadata
        lines_map = {}
        for w in words:
            line_idx = w.get("line_index", 0)
            if line_idx is None:
                line_idx = 0
            if line_idx not in lines_map:
                lines_map[line_idx] = []
            lines_map[line_idx].append(w)

        # 2. Retrieve font
        font_family = style.font_family
        font_size = style.font_size
        font = FontManager.load_truetype_font(font_family, font_size)

        # Prepare a dummy draw context to evaluate text boundary dimensions
        dummy_img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        # Space dimension metrics
        space_bbox = draw.textbbox((0, 0), " ", font=font)
        space_width = space_bbox[2] - space_bbox[0]

        line_layouts = []
        total_content_height = 0
        line_spacing_px = font_size * (style.line_spacing - 1.0)

        sorted_line_keys = sorted(lines_map.keys())

        # 3. Sum dimensions of words for each line
        for k in sorted_line_keys:
            line_words = lines_map[k]
            word_sizes = []
            line_width = 0
            max_word_height = 0

            for i, w in enumerate(line_words):
                word_text = w["word"]
                bbox = draw.textbbox((0, 0), word_text, font=font)
                w_width = bbox[2] - bbox[0]
                w_height = bbox[3] - bbox[1]

                word_sizes.append(
                    {"word_info": w, "width": w_width, "height": w_height}
                )

                line_width += w_width
                if i < len(line_words) - 1:
                    line_width += space_width + (style.letter_spacing or 0)
                max_word_height = max(max_word_height, w_height)

            line_layouts.append(
                {
                    "words": word_sizes,
                    "width": line_width,
                    "height": max_word_height,
                }
            )

            total_content_height += max_word_height

        total_content_height += (
            max(0, len(sorted_line_keys) - 1) * line_spacing_px
        )

        # 4. Resolve Vertical Y anchor positioning
        safe_margin = style.safe_margin

        if style.vertical_position == "top":
            y_start = safe_margin
        elif style.vertical_position == "center":
            y_start = (height - total_content_height) / 2.0
        else:  # bottom vertical position
            y_start = height - safe_margin - total_content_height

        # 5. Position coordinate calculations
        positioned_words = []
        current_y = y_start

        for layout in line_layouts:
            line_w = layout["width"]
            line_h = layout["height"]

            # Resolve Horizontal X anchor positioning
            if style.horizontal_position == "left":
                x_start = safe_margin
            elif style.horizontal_position == "right":
                x_start = width - safe_margin - line_w
            else:  # center horizontal position
                x_start = (width - line_w) / 2.0

            current_x = x_start

            for w_layout in layout["words"]:
                positioned_words.append(
                    {
                        "word": w_layout["word_info"]["word"],
                        "x": current_x,
                        "y": current_y,
                        "width": w_layout["width"],
                        "height": w_layout["height"],
                        "word_info": w_layout["word_info"],
                    }
                )
                current_x += (
                    w_layout["width"] + space_width + (style.letter_spacing or 0)
                )

            current_y += line_h + line_spacing_px

        return positioned_words
