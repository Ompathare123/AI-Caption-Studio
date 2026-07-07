from typing import Any, Dict, List


class AnimationPresets:

    @staticmethod
    def get_word_highlight(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @staticmethod
    def get_word_pop(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        # Pop scale from 1.0 to 1.35 to 1.0
        pop_duration = 0.15
        mid = start + pop_duration
        settle = start + (pop_duration * 2)

        if settle > end:
            settle = end
            mid = start + (end - start) / 2.0

        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(mid, 3),
                "scale": 1.35,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(settle, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @staticmethod
    def get_word_fade(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        # Fades in opacity from 0.0 to 1.0 at start
        fade_duration = 0.15
        fade_end = min(start + fade_duration, end)

        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 1.0,
                "opacity": 0.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 1.0,
                "opacity": 0.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(fade_end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 1.0,
                "opacity": 0.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @staticmethod
    def get_word_bounce(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        # Displaces Y coordinate vertically and bounces back down
        mid_bounce = start + 0.12
        settle_bounce = start + 0.25

        if settle_bounce > end:
            settle_bounce = end
            mid_bounce = start + (end - start) / 2.0

        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(mid_bounce, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": -15.0,
                "color": highlight_color,
            },
            {
                "time": round(settle_bounce, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @staticmethod
    def get_zoom_in(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        # Scale zooms from 0.0 to 1.0
        zoom_duration = 0.2
        zoom_end = min(start + zoom_duration, end)

        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 0.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 0.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(zoom_end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 0.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @staticmethod
    def get_zoom_out(
        start: float, end: float, text_color: str, highlight_color: str
    ) -> List[Dict[str, Any]]:
        # Scale zooms from 1.0 to 0.0 at the end of the word timeframe
        zoom_duration = 0.2
        zoom_start = max(start, end - zoom_duration)

        return [
            {
                "time": round(start - 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
            {
                "time": round(start, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(zoom_start, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end, 3),
                "scale": 0.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": highlight_color,
            },
            {
                "time": round(end + 0.01, 3),
                "scale": 1.0,
                "opacity": 1.0,
                "rotation": 0.0,
                "position_x": 0.0,
                "position_y": 0.0,
                "color": text_color,
            },
        ]

    @classmethod
    def generate_keyframes(
        cls,
        preset: str,
        start: float,
        end: float,
        text_color: str,
        highlight_color: str,
    ) -> List[Dict[str, Any]]:
        """
        Routes the target animation preset to its keyframe builder method.
        """
        p_clean = preset.lower().strip()

        # Group similar transitions under core presets builders
        if p_clean in ("word_highlight", "karaoke_highlight", "progress_fill"):
            return cls.get_word_highlight(
                start, end, text_color, highlight_color
            )
        elif p_clean in (
            "word_pop",
            "word_scale",
            "letter_animation",
            "character_animation",
            "sentence_pop",
        ):
            return cls.get_word_pop(start, end, text_color, highlight_color)
        elif p_clean in ("word_fade", "sentence_fade", "opacity_fade", "word_blur"):
            return cls.get_word_fade(start, end, text_color, highlight_color)
        elif p_clean in ("word_bounce", "word_slide", "word_rotate"):
            # Bounces vertically or rotates/slides depending on preset mapping
            keyframes = cls.get_word_bounce(
                start, end, text_color, highlight_color
            )
            if p_clean == "word_rotate":
                for k in keyframes:
                    if k["position_y"] == -15.0:
                        k["rotation"] = 15.0  # rotate instead of Y movement
                        k["position_y"] = 0.0
            elif p_clean == "word_slide":
                for k in keyframes:
                    if k["position_y"] == -15.0:
                        k["position_x"] = -30.0  # slide horizontally instead of Y movement
                        k["position_y"] = 0.0
            return keyframes
        elif p_clean == "zoom_in":
            return cls.get_zoom_in(start, end, text_color, highlight_color)
        elif p_clean == "zoom_out":
            return cls.get_zoom_out(start, end, text_color, highlight_color)
        else:
            return cls.get_word_highlight(
                start, end, text_color, highlight_color
            )
