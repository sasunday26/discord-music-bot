import { describe, expect, expectTypeOf, it, vi } from "vitest";
import { err, ok, type Result } from "./result.ts";

const succeeded: Result<number, "boom"> = ok(2);
const failed: Result<number, "boom"> = err("boom");

describe("ok", () => {
	it("wraps the value", () => {
		expect(ok(5)).toEqual({ kind: "ok", value: 5 });
		expectTypeOf(ok(5)).toEqualTypeOf<Result<number, never>>();
	});

	it("is assignable to a result with any error type", () => {
		expectTypeOf(ok(5)).toExtend<Result<number, string>>();
	});
});

describe("err", () => {
	it("wraps the error", () => {
		expect(err(Error("test"))).toEqual({ kind: "error", error: Error("test") });
		expectTypeOf(err(Error("test"))).toEqualTypeOf<Result<never, Error>>();
	});

	it("keeps string literal error types", () => {
		expectTypeOf(err("boom")).toEqualTypeOf<Result<never, "boom">>();
	});
});

describe("narrowing", () => {
	it("exposes value only after checking kind", () => {
		// @ts-expect-error value is not available on the error variant
		succeeded.value;

		if (succeeded.kind === "ok") {
			expectTypeOf(succeeded.value).toEqualTypeOf<number>();
		} else {
			expectTypeOf(succeeded.error).toEqualTypeOf<"boom">();
		}
	});

	it("is readonly", () => {
		const mutate = (r: Result<number, never>) => {
			if (r.kind === "ok") {
				// @ts-expect-error value is readonly
				r.value = 3;
			}
		};
		expectTypeOf(mutate).toBeFunction();
	});
});

describe("map", () => {
	it("transforms the success value", () => {
		expect(ok(2).map((x) => x * x)).toEqual(ok(4));
	});

	it("can change the value type", () => {
		expect(ok(4).map(String)).toEqual(ok("4"));
		expectTypeOf(succeeded.map(String)).toEqualTypeOf<Result<string, "boom">>();
	});

	it("passes errors through without calling f", () => {
		const f = vi.fn((n: number) => n * 2);

		expect(failed.map(f)).toEqual(err("boom"));
		expect(f).not.toHaveBeenCalled();
	});
});

describe("mapErr", () => {
	it("transforms the error", () => {
		expect(failed.mapErr((e) => e.toUpperCase())).toEqual(err("BOOM"));
	});

	it("can change the error type", () => {
		expectTypeOf(failed.mapErr((e) => ({ reason: e }))).toEqualTypeOf<
			Result<number, { reason: "boom" }>
		>();
	});

	it("passes success values through without calling f", () => {
		const f = vi.fn((e: "boom") => e.length);

		expect(succeeded.mapErr(f)).toEqual(ok(2));
		expect(f).not.toHaveBeenCalled();
	});
});

describe("andThen", () => {
	const positive = (n: number) => (n > 0 ? ok(n) : err("not-positive"));

	it("returns the result of a succeeding step", () => {
		expect(succeeded.andThen(positive)).toEqual(ok(2));
	});

	it("returns the error of a failing step", () => {
		expect(ok(-1).andThen(positive)).toEqual(err("not-positive"));
	});

	it("passes errors through without calling f", () => {
		const f = vi.fn(positive);

		expect(failed.andThen(f)).toEqual(err("boom"));
		expect(f).not.toHaveBeenCalled();
	});

	it("unions the error types of both steps", () => {
		expectTypeOf(succeeded.andThen(positive)).toEqualTypeOf<
			Result<number, "boom" | "not-positive">
		>();
	});

	it("short-circuits on the first failure", () => {
		const next = vi.fn((n: number) => ok(n + 1));

		expect(ok(-1).andThen(positive).andThen(next)).toEqual(err("not-positive"));
		expect(next).not.toHaveBeenCalled();
	});
});

describe("laws", () => {
	const double = (n: number) => ok(n * 2);

	it.each([succeeded, failed])("map identity: %o", (r) => {
		expect(r.map((x) => x)).toEqual(r);
	});

	it.each([succeeded, failed])("mapErr identity: %o", (r) => {
		expect(r.mapErr((e) => e)).toEqual(r);
	});

	it("left identity: ok(x).andThen(f) equals f(x)", () => {
		expect(ok(3).andThen(double)).toEqual(double(3));
	});

	it.each([succeeded, failed])("right identity: %o", (r) => {
		expect(r.andThen(ok)).toEqual(r);
	});
});
