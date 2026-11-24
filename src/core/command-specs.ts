import {
	type APIApplicationCommandOption,
	ApplicationCommandOptionType,
	type RESTPostAPIChatInputApplicationCommandsJSONBody,
} from "discord-api-types/v10";
import type { GuardPolicy } from "./guards.ts";
import { COMMAND_NAMES, type CommandName } from "./model.ts";
import { err, ok, type Result } from "./result.ts";

type MinValue = { readonly kind: "gte" | "gt"; readonly value: number };
type OptionSpec =
	| {
			readonly kind: "string";
			readonly name: string;
			readonly description: string;
			readonly required: true;
	  }
	| {
			readonly kind: "int" | "number";
			readonly name: string;
			readonly description: string;
			readonly required: true;
			readonly min?: MinValue;
			readonly max?: number;
	  }
	| {
			readonly kind: "int" | "number";
			readonly name: string;
			readonly description: string;
			readonly default: number;
			readonly required?: false;
			readonly min?: MinValue;
			readonly max?: number;
	  };

type CommandSpec = {
	readonly description: string;
	readonly guard: GuardPolicy;
	readonly options?: readonly OptionSpec[];
};

const toDiscordCommandsJson = (
	specs: Record<CommandName, CommandSpec>,
): RESTPostAPIChatInputApplicationCommandsJSONBody[] =>
	COMMAND_NAMES.map((n) => toDiscordCommand(n, specs[n]));

const toDiscordCommand = (
	name: CommandName,
	spec: CommandSpec,
): RESTPostAPIChatInputApplicationCommandsJSONBody => ({
	name: name,
	description: spec.description,
	...(spec.options !== undefined
		? { options: spec.options.map(toDiscordCommandOption) }
		: {}),
});

const toDiscordCommandOption = (
	option: OptionSpec,
): APIApplicationCommandOption => {
	const base = {
		name: option.name,
		description: option.description,
		required: option.required ?? false,
	};

	switch (option.kind) {
		case "string":
			return { ...base, type: ApplicationCommandOptionType.String };

		case "int":
			return {
				...base,
				type: ApplicationCommandOptionType.Integer,
				...(option.min !== undefined ? { min_value: option.min.value } : {}),
				...(option.max !== undefined ? { max_value: option.max } : {}),
			};

		case "number":
			return {
				...base,
				type: ApplicationCommandOptionType.Number,
				...(option.min !== undefined ? { min_value: option.min.value } : {}),
				...(option.max !== undefined ? { max_value: option.max } : {}),
			};
	}
};

type ParseError = "invalid-input" | "out-of-range";
type OptionError = {
	readonly optionName: string;
	readonly problem: ParseError;
};

const parseCommandOptions = (
	options: OptionSpec[],
	rawArgs: Readonly<Record<string, unknown>>,
): Result<Record<string, unknown>, OptionError> => {
	const initial: Result<Record<string, unknown>, OptionError> = ok({});

	return options.reduce(
		(acc, spec) =>
			acc.andThen((parsed) =>
				parseOption(spec, rawArgs[spec.name])
					.mapErr((error) => ({ optionName: spec.name, problem: error }))
					.map((value) => ({ ...parsed, [spec.name]: value })),
			),
		initial,
	);
};

const parseOption = (
	option: OptionSpec,
	raw: unknown,
): Result<number | string, ParseError> => {
	if (raw === undefined) {
		return "default" in option ? ok(option.default) : err("invalid-input");
	}

	switch (option.kind) {
		case "string":
			return parseStringOption(raw);

		case "int":
			return parseIntOption(option, raw);

		case "number":
			return parseNumberOption(option, raw);
	}
};

const parseStringOption = (raw: unknown): Result<string, ParseError> => {
	if (typeof raw !== "string") return err("invalid-input");
	const value = String(raw).trim();
	return value === "" ? err("invalid-input") : ok(value);
};

const parseIntOption = (
	option: Extract<OptionSpec, { kind: "int" | "number" }>,
	raw: unknown,
): Result<number, ParseError> =>
	parseNumber(raw)
		.andThen(requireSafeInteger)
		.andThen((v) => checkMin(v, option.min))
		.andThen((v) => checkMax(v, option.max));

const parseNumberOption = (
	option: Extract<OptionSpec, { kind: "int" | "number" }>,
	raw: unknown,
): Result<number, ParseError> =>
	parseNumber(raw)
		.andThen((v) => checkMin(v, option.min))
		.andThen((v) => checkMax(v, option.max));

const parseNumber = (raw: unknown): Result<number, ParseError> => {
	if (typeof raw !== "number") return err("invalid-input");
	const value = Number(raw);
	return Number.isFinite(value) ? ok(value) : err("invalid-input");
};

const requireSafeInteger = (value: number): Result<number, ParseError> =>
	Number.isSafeInteger(value) ? ok(value) : err("invalid-input");

const checkMin = (
	value: number,
	min: MinValue | undefined,
): Result<number, ParseError> => {
	if (min === undefined) return ok(value);
	switch (min.kind) {
		case "gte":
			return min.value > value ? err("out-of-range") : ok(value);
		case "gt":
			return min.value >= value ? err("out-of-range") : ok(value);
	}
};

const checkMax = (
	value: number,
	max: number | undefined,
): Result<number, ParseError> => {
	if (max === undefined) return ok(value);
	return value > max ? err("out-of-range") : ok(value);
};

const COMMAND_SPECS = {
	play: {
		description: "play a track or add it to queue if already playing",
		guard: "new-or-existing-session",
		options: [
			{
				kind: "string",
				name: "query",
				description: "track url or name",
				required: true,
			},
		],
	},
	pause: {
		description: "pause the current playing track",
		guard: "existing-session",
	},
	resume: {
		description: "resume the current playing track",
		guard: "existing-session",
	},
	now_playing: {
		description: "show the current playing track",
		guard: "existing-session",
	},
	queue: {
		description: "show the queue",
		guard: "existing-session",
	},
	clear: {
		description: "clear the queue (doesn't stop the current track)",
		guard: "existing-session",
	},
	skip: {
		description: "skip the current track",
		guard: "existing-session",
	},
	shut_the_fuck_up: {
		description: "stop playback and leave the voice channel",
		guard: "existing-session",
	},
	seek: {
		description: "seek to a position in the current track",
		guard: "existing-session",
		options: [
			{
				kind: "string",
				name: "position",
				description: "timestamp (HH:MM:SS, MM:SS, or seconds)",
				required: true,
			},
		],
	},
	volume: {
		description: "set the playback volume",
		guard: "existing-session",
		options: [
			{
				kind: "int",
				name: "volume",
				description: "volume level (0 to 1000)",
				required: true,
				min: { kind: "gte", value: 0 },
				max: 1000,
			},
		],
	},
	equalizer: {
		description: "adjust equalizer bands",
		guard: "existing-session",
		options: [
			{
				kind: "string",
				name: "settings",
				description:
					"space-separated band:gain pairs (band 0-14, gain -0.25 to 1.0)",
				required: true,
			},
		],
	},
	speed: {
		description: "adjust playback speed and pitch",
		guard: "existing-session",
		options: [
			{
				kind: "number",
				name: "speed",
				description: "playback speed multiplier (> 0)",
				required: true,
				min: { kind: "gt", value: 0 },
			},
			{
				kind: "number",
				name: "pitch",
				description: "playback pitch multiplier (> 0)",
				default: 1.0,
				min: { kind: "gt", value: 0 },
			},
		],
	},
	slowreverb: {
		description: "apply slowed and reverb effect",
		guard: "existing-session",
		options: [
			{
				kind: "number",
				name: "speed",
				description: "playback speed multiplier (0.1 to 2.0)",
				default: 0.85,
				min: { kind: "gte", value: 0.1 },
				max: 2.0,
			},
			{
				kind: "number",
				name: "pitch",
				description: "playback pitch multiplier (0.1 to 2.0)",
				default: 0.85,
				min: { kind: "gte", value: 0.1 },
				max: 2.0,
			},
			{
				kind: "number",
				name: "echo_length",
				description: "echo length (0 to 1)",
				default: 0.15,
				min: { kind: "gte", value: 0 },
				max: 1,
			},
			{
				kind: "number",
				name: "decay",
				description: "echo decay (0 to 1)",
				default: 0.4,
				min: { kind: "gte", value: 0 },
				max: 1,
			},
			{
				kind: "number",
				name: "cutoff",
				description: "low-pass cutoff frequency in Hz (100 to 20000)",
				default: 1500,
				min: { kind: "gte", value: 100 },
				max: 20000,
			},
		],
	},
	reset_filters: {
		description: "reset all audio filters and volume",
		guard: "existing-session",
	},
	outro: {
		description: "play the outro and disconnect everyone",
		guard: "existing-session",
	},
} as const satisfies Record<CommandName, CommandSpec>;
