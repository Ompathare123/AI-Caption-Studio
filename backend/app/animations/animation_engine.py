from typing import Any, Dict, List

from backend.app.animations.animation_presets import AnimationPresets
from backend.app.schemas.caption_style import StyleProperties


class AnimationEngine:

    @staticmethod
    def generate_animation_timeline(
        subtitles: List[Dict[str, Any]], style: StyleProperties, preset: str
    ) -> List[Dict[str, Any]]:
        """
        Compiles raw subtitle segments into animated word elements with detailed
        transition keyframe lists mapped to absolute timestamps.
        """
        animated_segments = []

        text_color = style.text_color
        highlight_color = style.highlight_color
        shadow_color = style.shadow_color if style.shadow_color else "#000000"

        for seg in subtitles:
            animated_words = []
            for w in seg.get("words", []):
                start = w.get("start")
                end = w.get("end")
                word_text = w.get("word")

                # Fallback to parent segment times if word timestamps are missing
                if start is None:
                    start = seg.get("start", 0.0)
                if end is None:
                    end = seg.get("end", start + 0.3)

                # Compile keyframes sequence for this word spoken duration
                keyframes = AnimationPresets.generate_keyframes(
                    preset=preset,
                    start=start,
                    end=end,
                    text_color=text_color,
                    highlight_color=highlight_color,
                )

                # Assemble animated word schema properties
                animated_word = {
                    "word": word_text,
                    "start": start,
                    "end": end,
                    "animation_type": preset,
                    "scale": 1.0,
                    "opacity": 1.0,
                    "rotation": 0.0,
                    "position_x": 0.0,
                    "position_y": 0.0,
                    "color": text_color,
                    "highlight_color": highlight_color,
                    "shadow_color": shadow_color,
                    "keyframes": keyframes,
                }
                animated_words.append(animated_word)

            animated_segments.append(
                {
                    "index": seg.get("index"),
                    "start": seg.get("start"),
                    "end": seg.get("end"),
                    "text": seg.get("text"),
                    "words": animated_words,
                }
            )

        return animated_segments
