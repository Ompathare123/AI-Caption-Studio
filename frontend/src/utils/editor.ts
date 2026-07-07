import type { AlignmentSegment } from "../services/api";

export const splitSegment = (
  segments: AlignmentSegment[],
  index: number,
  splitTime: number
): AlignmentSegment[] => {
  const seg = segments[index];
  if (splitTime <= seg.start || splitTime >= seg.end) {
    return segments;
  }

  const firstWords = seg.words.filter((w) => w.end <= splitTime);
  const secondWords = seg.words.filter((w) => w.end > splitTime);

  const firstText = firstWords.map((w) => w.word).join(" ");
  const secondText = secondWords.map((w) => w.word).join(" ");

  const firstSeg: AlignmentSegment = {
    text: firstText || "First",
    start: seg.start,
    end: splitTime,
    words: firstWords.length > 0 ? firstWords : [{ word: "First", start: seg.start, end: splitTime, score: 1.0 }],
  };

  const secondSeg: AlignmentSegment = {
    text: secondText || "Second",
    start: splitTime,
    end: seg.end,
    words: secondWords.length > 0 ? secondWords : [{ word: "Second", start: splitTime, end: seg.end, score: 1.0 }],
  };

  const updated = [...segments];
  updated.splice(index, 1, firstSeg, secondSeg);
  return updated;
};

export const mergeSegments = (
  segments: AlignmentSegment[],
  index: number
): AlignmentSegment[] => {
  if (index >= segments.length - 1) return segments;
  const current = segments[index];
  const next = segments[index + 1];

  const mergedSeg: AlignmentSegment = {
    text: `${current.text} ${next.text}`,
    start: current.start,
    end: next.end,
    words: [...current.words, ...next.words],
  };

  const updated = [...segments];
  updated.splice(index, 2, mergedSeg);
  return updated;
};
