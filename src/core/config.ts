import { err, ok, type Result } from "./result.ts";

type ConfigError = {
	readonly variable: string;
	readonly problem: "missing" | "invalid";
};

const LOG_LEVELS = ["debug", "info", "warn", "error"] as const;
type LogLevel = (typeof LOG_LEVELS)[number];

type BotConfig = {
	readonly discord: {
		readonly botToken: string;
	};
	readonly lavalink: {
		readonly url: string;
		readonly secure: boolean;
		readonly password: string;
	};
	readonly outro: {
		readonly url: string;
		readonly timestampMs: number;
	};
	readonly log: { readonly level: LogLevel };
	readonly leaveEmptyChannelAfterSec: number;
};

type Env = Readonly<Record<string, string | undefined>>;

const field = <T>(
	env: Env,
	variable: string,
	parse: (raw: string) => Result<T, unknown>,
): Result<T, ConfigError> => {
	const raw = env[variable];
	if (raw === undefined || raw === "") {
		return err({ variable, problem: "missing" });
	}

	return parse(raw).mapErr(() => ({ variable, problem: "invalid" }));
};

const text = (raw: string) => ok(raw);

const positiveInt = (raw: string): Result<number, "invalid"> => {
	const value = Number(raw);
	return /^\d+$/.test(raw) && Number.isSafeInteger(value) && value > 0
		? ok(value)
		: err("invalid");
};

const httpUrl = (raw: string): Result<URL, "invalid"> => {
	const url = URL.parse(raw);
	return url !== null && (url.protocol === "http:" || url.protocol === "https:")
		? ok(url)
		: err("invalid");
};

const lavalinkUri = (raw: string) =>
	httpUrl(raw).andThen((url) =>
		url.pathname === "/" && url.search === "" && url.hash === ""
			? ok({ url: url.host, secure: url.protocol === "https:" })
			: err("invalid"),
	);

const isLogLevel = (raw: string): raw is LogLevel =>
	LOG_LEVELS.some((level) => level === raw);

const logLevel = (raw: string): Result<LogLevel, "invalid"> =>
	isLogLevel(raw) ? ok(raw) : err("invalid");

const parseBotConfig = (env: Env): Result<BotConfig, ConfigError> => {
	const botToken = field(env, "DISCORD_BOT_TOKEN", text);
	if (botToken.isErr()) return err(botToken.error);

	const lavalink = field(env, "LAVALINK_URI", lavalinkUri);
	if (lavalink.isErr()) return err(lavalink.error);

	const lavalinkPassword = field(env, "LAVALINK_PASSWORD", text);
	if (lavalinkPassword.isErr()) return err(lavalinkPassword.error);

	const outroUrl = field(env, "OUTRO_VIDEO_URL", (raw) =>
		httpUrl(raw).map((url) => url.href),
	);
	if (outroUrl.isErr()) return err(outroUrl.error);

	const outroTimestampMs = field(env, "OUTRO_VIDEO_TIMESTAMP_MS", positiveInt);
	if (outroTimestampMs.isErr()) return err(outroTimestampMs.error);

	const leaveAfterSec = field(
		env,
		"LEAVE_EMPTY_CHANNEL_AFTER_SEC",
		positiveInt,
	);
	if (leaveAfterSec.isErr()) return err(leaveAfterSec.error);

	const level = env.LOG_LEVEL
		? field(env, "LOG_LEVEL", logLevel)
		: ok<LogLevel>("info");
	if (level.isErr()) return err(level.error);

	return ok({
		discord: { botToken: botToken.value },
		lavalink: { ...lavalink.value, password: lavalinkPassword.value },
		outro: { url: outroUrl.value, timestampMs: outroTimestampMs.value },
		log: { level: level.value },
		leaveEmptyChannelAfterSec: leaveAfterSec.value,
	});
};

type RegisterCommandsConfig = {
	readonly discord: {
		readonly botToken: string;
		readonly clientId: string;
	};
};

const parseRegisterCommandsConfig = (
	env: Env,
): Result<RegisterCommandsConfig, ConfigError> => {
	const botToken = field(env, "DISCORD_BOT_TOKEN", text);
	if (botToken.isErr()) return err(botToken.error);

	const clientId = field(env, "DISCORD_CLIENT_ID", text);
	if (clientId.isErr()) return err(clientId.error);

	return ok({
		discord: { botToken: botToken.value, clientId: clientId.value },
	});
};

export {
	type BotConfig,
	type ConfigError,
	type LogLevel,
	parseBotConfig,
	parseRegisterCommandsConfig,
	type RegisterCommandsConfig,
};
