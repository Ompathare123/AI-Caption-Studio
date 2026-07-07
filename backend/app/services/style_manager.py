import re
from typing import Any, Dict, List

EMOJI_MAP = {
    "fire": "🔥",
    "money": "💰",
    "cash": "💵",
    "love": "❤️",
    "heart": "❤️",
    "happy": "😊",
    "lol": "😂",
    "laugh": "😂",
    "game": "🎮",
    "play": "🎮",
    "star": "⭐",
    "cool": "😎",
    "wow": "😮",
    "mindblown": "🤯",
    "shocked": "😱",
    "rocket": "🚀",
    "time": "⏰",
    "alert": "🚨",
    "warning": "⚠️",
    "stop": "🛑",
}


class StyleManager:

    @staticmethod
    def scale_style(
        style_data: Dict[str, Any], width: int, aspect_ratio: str
    ) -> Dict[str, Any]:
        """
        Proportionally scale font sizes, outline widths, padding, margins based on aspect ratios.
        Base scale calculations are compared against standard 1080p width dimensions.
        """
        scaled = dict(style_data)

        # Establish base reference width dimensions
        if aspect_ratio == "horizontal":
            ref_width = 1920
        elif aspect_ratio == "vertical":
            ref_width = 1080
        else:  # square aspect ratio
            ref_width = 1080

        scale_factor = width / ref_width

        # Apply scaling multipliers
        scaled["font_size"] = round(scaled["font_size"] * scale_factor, 2)
        scaled["outline_width"] = round(
            scaled["outline_width"] * scale_factor, 2
        )
        scaled["shadow_offset_x"] = round(
            scaled["shadow_offset_x"] * scale_factor, 2
        )
        scaled["shadow_offset_y"] = round(
            scaled["shadow_offset_y"] * scale_factor, 2
        )
        scaled["padding"] = round(scaled["padding"] * scale_factor, 2)
        scaled["border_radius"] = round(
            scaled["border_radius"] * scale_factor, 2
        )
        scaled["safe_margin"] = round(scaled["safe_margin"] * scale_factor, 2)

        return scaled

    @staticmethod
    def apply_text_effects(
        segment: Dict[str, Any], effects: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply text casing, automatic sentence capitalization, and context emojis.
        Reconstructs the segment's full text body from the styled words list.
        """
        casing = effects.get("case", "normal")
        auto_cap = effects.get("auto_capitalization", True)
        auto_emoji = effects.get("auto_emoji", False)

        words_copy = [dict(w) for w in segment.get("words", [])]

        for w in words_copy:
            clean_word = w["word"].strip()

            # 1. Casing transformations
            if casing == "uppercase":
                clean_word = clean_word.upper()
            elif casing == "lowercase":
                clean_word = clean_word.lower()
            elif casing == "titlecase":
                clean_word = clean_word.title()

            # 2. Auto Emoji mappings
            if auto_emoji:
                base_word = re.sub(r"[^\w]", "", clean_word.lower())
                if base_word in EMOJI_MAP:
                    emoji = EMOJI_MAP[base_word]
                    if emoji not in clean_word:
                        clean_word = f"{clean_word} {emoji}"

            w["word"] = clean_word

        # 3. Reconstruct segment text grouping by line index
        lines_map = {}
        for w in words_copy:
            line_idx = w.get("line_index", 0)
            if line_idx is None:
                line_idx = 0
            if line_idx not in lines_map:
                lines_map[line_idx] = []
            lines_map[line_idx].append(w["word"])

        sorted_lines = [
            " ".join(lines_map[k]) for k in sorted(lines_map.keys())
        ]
        full_text = "\n".join(sorted_lines)

        # 4. Auto Capitalization (only applied if base text casing is normal)
        if auto_cap and casing == "normal":
            sentences = re.split(r"([.!?]\s*)", full_text)
            capitalized = []
            for part in sentences:
                if part and part[0].isalpha():
                    part = part[0].upper() + part[1:]
                capitalized.append(part)
            full_text = "".join(capitalized)

        segment_copy = dict(segment)
        segment_copy["text"] = full_text
        segment_copy["words"] = words_copy
        return segment_copy
