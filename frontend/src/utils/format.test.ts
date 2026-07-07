import { expect, test } from "vitest";
import { formatSize, formatDuration } from "./format";

test("formatSize formats bytes to readable sizes", () => {
  expect(formatSize(0)).toBe("0 Bytes");
  expect(formatSize(1024)).toBe("1 KB");
  expect(formatSize(1048576)).toBe("1 MB");
});

test("formatDuration formats seconds to mm:ss", () => {
  expect(formatDuration(0)).toBe("0:00");
  expect(formatDuration(65)).toBe("1:05");
  expect(formatDuration(3600)).toBe("60:00");
});
