import math
from typing import Dict, List


class SubtitleBuilder:

    @staticmethod
    def interpolate_timestamps(words: List[Dict]) -> List[Dict]:
        """
        Interpolate missing timestamps to handle unaligned words gracefully.
        """
        n = len(words)
        if n == 0:
            return words

        # Copy list to prevent mutating original data
        words = [dict(w) for w in words]

        for i in range(n):
            if words[i].get("start") is None:
                if i > 0 and words[i - 1].get("end") is not None:
                    words[i]["start"] = words[i - 1]["end"]
                else:
                    # Look forward for first valid start time
                    forward_start = None
                    for j in range(i + 1, n):
                        if words[j].get("start") is not None:
                            forward_start = words[j]["start"]
                            break
                    words[i]["start"] = (
                        forward_start if forward_start is not None else 0.0
                    )

            if words[i].get("end") is None:
                if i < n - 1 and words[i + 1].get("start") is not None:
                    words[i]["end"] = words[i + 1]["start"]
                else:
                    words[i]["end"] = words[i]["start"] + 0.3

        return words

    @staticmethod
    def build_captions(
        words: List[Dict],
        max_words_per_line: int = 5,
        max_lines: int = 2,
        reading_speed: int = 18,
    ) -> List[Dict]:
        """
        Groups aligned words into structured subtitle captions following readability
        constraints (words per line, line count, sentence breaks, reading speed).
        """
        words = SubtitleBuilder.interpolate_timestamps(words)
        if not words:
            return []

        max_words_per_caption = max_words_per_line * max_lines
        captions = []
        current_words = []

        for i, word_info in enumerate(words):
            word = word_info["word"]
            current_words.append(word_info)

            break_caption = False

            # Rule 1: Max words reached
            if len(current_words) >= max_words_per_caption:
                break_caption = True

            # Rule 2: Split at end-of-sentence punctuation
            elif word.endswith((".", "?", "!")):
                break_caption = True

            # Rule 3: Split if silence/gap to next word is large (> 1.0 second)
            elif i < len(words) - 1:
                next_word = words[i + 1]
                if (
                    next_word.get("start") is not None
                    and word_info.get("end") is not None
                ):
                    gap = next_word["start"] - word_info["end"]
                    if gap > 1.0:
                        break_caption = True

            # Rule 4: Split at weak punctuation (comma, colon) if line is full
            elif word.endswith((",", ";", ":")) and len(current_words) >= max_words_per_line:
                break_caption = True

            if break_caption or i == len(words) - 1:
                captions.append(current_words)
                current_words = []

        # Catch remaining words
        if current_words:
            captions.append(current_words)

        formatted_captions = []
        for index, cap_words in enumerate(captions):
            if not cap_words:
                continue

            total_words = len(cap_words)
            lines = []

            # Balance line word distribution (avoid trailing single-word lines)
            if total_words <= max_words_per_line:
                lines.append(cap_words)
            else:
                split_idx = math.ceil(total_words / 2)
                lines.append(cap_words[:split_idx])
                lines.append(cap_words[split_idx:])

            text_lines = []
            words_list = []
            line_idx = 0

            for line_words in lines:
                line_text = " ".join([w["word"] for w in line_words])
                text_lines.append(line_text)
                for w in line_words:
                    words_list.append(
                        {
                            "word": w["word"],
                            "start": w["start"],
                            "end": w["end"],
                            "confidence": w.get("confidence", 1.0),
                            "line_index": line_idx,
                            "caption_index": index,
                        }
                    )
                line_idx += 1

            full_text = "\n".join(text_lines)
            start_time = cap_words[0]["start"]
            end_time = cap_words[-1]["end"]

            formatted_captions.append(
                {
                    "index": index + 1,
                    "start": round(start_time, 3),
                    "end": round(end_time, 3),
                    "text": full_text,
                    "words": words_list,
                }
            )

        # Enforce reading speed (expand start/end outward to lower characters-per-second)
        for idx in range(len(formatted_captions)):
            cap = formatted_captions[idx]
            text_len = len(cap["text"].replace("\n", " ").strip())
            req_dur = text_len / reading_speed
            curr_dur = cap["end"] - cap["start"]

            if curr_dur < req_dur:
                deficit = req_dur - curr_dur
                next_start = (
                    formatted_captions[idx + 1]["start"]
                    if idx < len(formatted_captions) - 1
                    else float("inf")
                )
                prev_end = (
                    formatted_captions[idx - 1]["end"] if idx > 0 else 0.0
                )

                # 1. Expand end forward first
                max_extend = next_start - cap["end"]
                extend_by = min(deficit, max(0.0, max_extend - 0.05))
                cap["end"] = round(cap["end"] + extend_by, 3)

                deficit -= extend_by
                if deficit > 0:
                    # 2. Expand start backward
                    max_pre_extend = cap["start"] - prev_end
                    pre_extend_by = min(deficit, max(0.0, max_pre_extend - 0.05))
                    cap["start"] = round(cap["start"] - pre_extend_by, 3)

        return formatted_captions
