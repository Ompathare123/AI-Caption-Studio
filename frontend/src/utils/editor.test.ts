import { expect, test } from "vitest";
import { splitSegment, mergeSegments } from "./editor";
import type { AlignmentSegment } from "../services/api";

const mockSegments: AlignmentSegment[] = [
  {
    text: "hello world",
    start: 0.0,
    end: 2.0,
    words: [
      { word: "hello", start: 0.0, end: 1.0, score: 1.0 },
      { word: "world", start: 1.0, end: 2.0, score: 1.0 },
    ],
  },
  {
    text: "next segment",
    start: 2.0,
    end: 4.0,
    words: [
      { word: "next", start: 2.0, end: 3.0, score: 1.0 },
      { word: "segment", start: 3.0, end: 4.0, score: 1.0 },
    ],
  },
];

test("splitSegment splits segment by time", () => {
  const result = splitSegment(mockSegments, 0, 1.0);
  expect(result.length).toBe(3);
  expect(result[0].text).toBe("hello");
  expect(result[0].end).toBe(1.0);
  expect(result[1].text).toBe("world");
  expect(result[1].start).toBe(1.0);
});

test("mergeSegments merges adjacent segments", () => {
  const result = mergeSegments(mockSegments, 0);
  expect(result.length).toBe(1);
  expect(result[0].text).toBe("hello world next segment");
  expect(result[0].start).toBe(0.0);
  expect(result[0].end).toBe(4.0);
});
