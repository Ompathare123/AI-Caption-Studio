import json
from typing import Dict, List


class SubtitleFormatter:

    @staticmethod
    def format_srt_time(seconds: float) -> str:
        """
        Convert float seconds into SRT timestamp string format: HH:MM:SS,mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))

        if millis >= 1000:
            secs += 1
            millis -= 1000
        if secs >= 60:
            minutes += 1
            secs -= 60
        if minutes >= 60:
            hours += 1
            minutes -= 60

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_ass_time(seconds: float) -> str:
        """
        Convert float seconds into ASS timestamp string format: H:MM:SS.cs
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds - int(seconds)) * 100))

        if centis >= 100:
            secs += 1
            centis -= 100
        if secs >= 60:
            minutes += 1
            secs -= 60
        if minutes >= 60:
            hours += 1
            minutes -= 60

        return f"{hours:d}:{minutes:02d}:{secs:02d}.{centis:02d}"

    @staticmethod
    def to_srt(captions: List[Dict]) -> str:
        """
        Format caption list into standard SubRip (.srt) string.
        """
        lines = []
        for cap in captions:
            lines.append(str(cap["index"]))
            start = SubtitleFormatter.format_srt_time(cap["start"])
            end = SubtitleFormatter.format_srt_time(cap["end"])
            lines.append(f"{start} --> {end}")
            lines.append(cap["text"])
            lines.append("")  # Empty line separator

        return "\n".join(lines)

    @staticmethod
    def to_ass(captions: List[Dict], style: str = "default") -> str:
        """
        Format caption list into Advanced SubStation Alpha (.ass) string.
        """
        # Set up a v4.00+ Script template styling header
        ass_header = (
            "[Script Info]\n"
            "Title: AI Caption Studio Generated Subtitles\n"
            "ScriptType: v4.00+\n"
            "WrapStyle: 0\n"
            "PlayResX: 640\n"
            "PlayResY: 360\n"
            "ScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
            "-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
            "Effect, Text\n"
        )

        dialogue_lines = []
        for cap in captions:
            start = SubtitleFormatter.format_ass_time(cap["start"])
            end = SubtitleFormatter.format_ass_time(cap["end"])
            # ASS uses uppercase \N for forced line breaks
            text_ass = cap["text"].replace("\n", "\\N")
            dialogue_lines.append(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text_ass}"
            )

        return ass_header + "\n".join(dialogue_lines) + "\n"

    @staticmethod
    def to_json(captions: List[Dict]) -> str:
        """
        Format caption list into structured JSON string.
        """
        structured_data = []
        for cap in captions:
            structured_data.append(
                {
                    "index": cap["index"],
                    "start": cap["start"],
                    "end": cap["end"],
                    "text": cap["text"],
                    "words": cap["words"],
                }
            )
        return json.dumps(structured_data, indent=2, ensure_ascii=False)
