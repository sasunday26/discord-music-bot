import { err, ok, type Result } from "./result.ts";

type DurationError = "invalid-format" | "out-of-range";

const isWithinLimit = (
  value: number,
  max: number,
): Result<number, DurationError> =>
  Number.isSafeInteger(value) && value < max ? ok(value) : err("out-of-range");

const PATTERN: RegExp =
  /^((?:(?<hours>\d+):)?(?<minutes>\d{1,2}):)?(?<seconds>\d+)$/;

const parseTimestampToMs = (input: string): Result<number, DurationError> => {
  const groups = input.trim().match(PATTERN)?.groups;
  if (groups === undefined) return err("invalid-format");

  const { hours, minutes, seconds } = groups;
  const secondsMax = minutes === undefined ? Infinity : 60;

  return isWithinLimit(Number(hours ?? 0), Infinity)
    .andThen((h) =>
      isWithinLimit(Number(minutes ?? 0), 60).andThen((m) =>
        isWithinLimit(Number(seconds ?? 0), secondsMax).map(
          (s) => (h * 3600 + m * 60 + s) * 1000,
        ),
      ),
    )
    .andThen((ms) => isWithinLimit(ms, Infinity));
};

const pad = (n: number): string => String(n).padStart(2, "0");

const formatDurationMs = (ms: number): string => {
  const totalSeconds =
    Number.isFinite(ms) && ms > 0 ? Math.floor(ms / 1000) : 0;
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const minutesAndSeconds = `${pad(minutes)}:${pad(seconds)}`;

  return hours > 0 ? `${pad(hours)}:${minutesAndSeconds}` : minutesAndSeconds;
};

export { formatDurationMs, parseTimestampToMs };
