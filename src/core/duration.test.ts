import { describe, expect, it } from "vitest";
import { formatDurationMs, parseTimestampToMs } from "./duration.ts";
import { err, ok } from "./result.ts";

describe("parseTimestampToMs", () => {
	it.each([
		["01:23:30", 5_010_000],
		["23:59", 1_439_000],
		["4:20:00", 15_600_000],
		["3123", 3_123_000],
		["   2:30   ", 150_000],
	])("parses %s", (input, expected) => {
		expect(parseTimestampToMs(input)).toEqual(ok(expected));
	});

	it.each([
		["", "invalid-format"],
		["abc", "invalid-format"],
		["4:75", "out-of-range"],
		["99:10", "out-of-range"],
		["99999999999999999999999999999999999:10", "invalid-format"],
		["9999999999999999999999999999999999999", "out-of-range"],
	])("rejects %s", (input, expected) => {
		expect(parseTimestampToMs(input)).toEqual(err(expected));
	});
});

describe("formatDurationMs", () => {
	it.each([
		[0, "00:00"],
		[999, "00:00"],
		[65_000, "01:05"],
		[3_599_999, "59:59"],
		[3_600_000, "01:00:00"],
		[3_723_000, "01:02:03"],
		[360_000_000, "100:00:00"],
	])("formats %d ms as %s", (ms, expected) => {
		expect(formatDurationMs(ms)).toBe(expected);
	});

	it.each([-1, Number.NaN, Number.POSITIVE_INFINITY])(
		"formats invalid input %d as 00:00",
		(ms) => {
			expect(formatDurationMs(ms)).toBe("00:00");
		},
	);
});

describe("round-trip", () => {
	it.each([0, 65_999, 3_723_000, 359_999_999, 360_000_000])(
		"%d ms through format and parse, truncated to seconds",
		(ms) => {
			expect(parseTimestampToMs(formatDurationMs(ms))).toEqual(
				ok(Math.floor(ms / 1000) * 1000),
			);
		},
	);
});
