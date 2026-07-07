from typing import Any, Dict, List


class TimelineGenerator:

    @staticmethod
    def calculate_total_duration(subtitles: List[Dict[str, Any]]) -> float:
        """
        Calculates the total timeline duration from the maximum subtitle end stamp.
        """
        if not subtitles:
            return 0.0
        return max([seg.get("end", 0.0) for seg in subtitles])

    @staticmethod
    def compile_word_intervals(segment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts all word timings inside a parent segment window.
        """
        intervals = []
        for w in segment.get("words", []):
            intervals.append(
                {
                    "word": w.get("word"),
                    "start": w.get("start"),
                    "end": w.get("end"),
                }
            )
        return intervals
