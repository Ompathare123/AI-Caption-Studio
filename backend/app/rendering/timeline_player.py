from typing import Any, Dict, List, Optional


class TimelinePlayer:

    @staticmethod
    def get_active_segment(
        timeline: List[Dict[str, Any]], t: float
    ) -> Optional[Dict[str, Any]]:
        """
        Scan and return the segment active at absolute timestamp t.
        """
        for seg in timeline:
            if seg["start"] <= t <= seg["end"]:
                return seg
        return None

    @staticmethod
    def interpolate_value(v1: float, v2: float, progress: float) -> float:
        return v1 + (v2 - v1) * progress

    @staticmethod
    def interpolate_color(c1: str, c2: str, progress: float) -> str:
        """
        Linear interpolates RGB channels between two HEX color strings.
        """
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)

            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)

            # Safeguard channels boundaries
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            return f"#{r:02x}{g:02x}{b:02x}".upper()
        except Exception:
            return c1

    @staticmethod
    def get_word_properties_at_time(
        word_info: Dict[str, Any], t: float
    ) -> Dict[str, Any]:
        """
        Evaluate and return the exact interpolated visual property states
        of a word at timestamp t using its keyframes sequence.
        """
        keyframes = word_info.get("keyframes", [])

        default_state = {
            "scale": word_info.get("scale", 1.0),
            "opacity": word_info.get("opacity", 1.0),
            "rotation": word_info.get("rotation", 0.0),
            "position_x": word_info.get("position_x", 0.0),
            "position_y": word_info.get("position_y", 0.0),
            "color": word_info.get("color", "#FFFFFF"),
        }

        if not keyframes:
            return default_state

        # Case 1: Before first keyframe
        if t <= keyframes[0]["time"]:
            return {
                "scale": keyframes[0].get("scale", 1.0),
                "opacity": keyframes[0].get("opacity", 1.0),
                "rotation": keyframes[0].get("rotation", 0.0),
                "position_x": keyframes[0].get("position_x", 0.0),
                "position_y": keyframes[0].get("position_y", 0.0),
                "color": keyframes[0].get("color", "#FFFFFF"),
            }

        # Case 2: After last keyframe
        if t >= keyframes[-1]["time"]:
            return {
                "scale": keyframes[-1].get("scale", 1.0),
                "opacity": keyframes[-1].get("opacity", 1.0),
                "rotation": keyframes[-1].get("rotation", 0.0),
                "position_x": keyframes[-1].get("position_x", 0.0),
                "position_y": keyframes[-1].get("position_y", 0.0),
                "color": keyframes[-1].get("color", "#FFFFFF"),
            }

        # Case 3: Interpolate between bounding frames
        for i in range(len(keyframes) - 1):
            kf1 = keyframes[i]
            kf2 = keyframes[i + 1]
            if kf1["time"] <= t <= kf2["time"]:
                duration = kf2["time"] - kf1["time"]
                if duration <= 0:
                    return kf2

                progress = (t - kf1["time"]) / duration

                return {
                    "scale": TimelinePlayer.interpolate_value(
                        kf1.get("scale", 1.0), kf2.get("scale", 1.0), progress
                    ),
                    "opacity": TimelinePlayer.interpolate_value(
                        kf1.get("opacity", 1.0), kf2.get("opacity", 1.0), progress
                    ),
                    "rotation": TimelinePlayer.interpolate_value(
                        kf1.get("rotation", 0.0), kf2.get("rotation", 0.0), progress
                    ),
                    "position_x": TimelinePlayer.interpolate_value(
                        kf1.get("position_x", 0.0),
                        kf2.get("position_x", 0.0),
                        progress,
                    ),
                    "position_y": TimelinePlayer.interpolate_value(
                        kf1.get("position_y", 0.0),
                        kf2.get("position_y", 0.0),
                        progress,
                    ),
                    "color": TimelinePlayer.interpolate_color(
                        kf1["color"], kf2["color"], progress
                    ),
                }

        return default_state
