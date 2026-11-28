import { describe, expect, it } from "vitest";
import {
	evaluateGuardPolicy,
	type GuardError,
	type GuardPolicy,
} from "./guards.ts";
import type { CommandCtx, GuildSession, VoiceChannel } from "./model.ts";
import { err, ok } from "./result.ts";

const session: GuildSession = {
	guildId: "guild",
	voiceChannelId: "session-voice",
	homeChannelId: "home-text",
	state: { status: "idle" },
	queue: [],
	volume: 100,
	filters: { equalizer: new Map() },
	emptySinceMs: undefined,
};

const voiceChannel: VoiceChannel = {
	id: "session-voice",
	botCanJoin: true,
	botCanSpeak: true,
};

const ctx: CommandCtx = {
	interactionId: "interaction",
	guildId: "guild",
	channelId: "home-text",
	voiceChannel,
	nowMs: 0,
};

describe.each<GuardPolicy>(["existing-session", "new-or-existing-session"])(
	"%s with an active session",
	(policy) => {
		it("returns the session when the caller is in its voice and text channels", () => {
			expect(evaluateGuardPolicy(policy, session, ctx)).toEqual(
				ok({ kind: "existing-session", session }),
			);
		});

		it("does not check bot voice permissions", () => {
			const noPermissions: CommandCtx = {
				...ctx,
				voiceChannel: {
					...voiceChannel,
					botCanJoin: false,
					botCanSpeak: false,
				},
			};
			expect(evaluateGuardPolicy(policy, session, noPermissions)).toEqual(
				ok({ kind: "existing-session", session }),
			);
		});

		it.each<[string, GuardError, Partial<CommandCtx>]>([
			[
				"a caller outside any voice channel",
				"user-not-in-voice-channel",
				{ voiceChannel: undefined },
			],
			[
				"a command from another text channel",
				"different-text-channel",
				{ channelId: "other-text" },
			],
			[
				"a caller in another voice channel",
				"different-voice-channel",
				{ voiceChannel: { ...voiceChannel, id: "other-voice" } },
			],
		])("rejects %s with %s", (_, expected, overrides) => {
			expect(
				evaluateGuardPolicy(policy, session, { ...ctx, ...overrides }),
			).toEqual(err(expected));
		});

		it.each<[string, GuardError, Partial<CommandCtx>]>([
			[
				"outside any voice channel and in another text channel",
				"user-not-in-voice-channel",
				{ voiceChannel: undefined, channelId: "other-text" },
			],
			[
				"in another voice channel and another text channel",
				"different-text-channel",
				{
					voiceChannel: { ...voiceChannel, id: "other-voice" },
					channelId: "other-text",
				},
			],
		])("reports a caller %s as %s", (_, expected, overrides) => {
			expect(
				evaluateGuardPolicy(policy, session, { ...ctx, ...overrides }),
			).toEqual(err(expected));
		});
	},
);

describe("existing-session without a session", () => {
	it("rejects with no-active-session", () => {
		expect(evaluateGuardPolicy("existing-session", undefined, ctx)).toEqual(
			err("no-active-session"),
		);
	});

	it("reports no-active-session before any other failure", () => {
		const failsEverything: CommandCtx = {
			...ctx,
			channelId: "other-text",
			voiceChannel: undefined,
		};
		expect(
			evaluateGuardPolicy("existing-session", undefined, failsEverything),
		).toEqual(err("no-active-session"));
	});
});

describe("new-or-existing-session without a session", () => {
	it("returns the caller's voice channel", () => {
		expect(
			evaluateGuardPolicy("new-or-existing-session", undefined, {
				...ctx,
				voiceChannel: { ...voiceChannel, id: "caller-voice" },
			}),
		).toEqual(
			ok({ kind: "new-session", callerVoiceChannelId: "caller-voice" }),
		);
	});

	it.each<[string, Partial<VoiceChannel>]>([
		["join", { botCanJoin: false }],
		["speak", { botCanSpeak: false }],
		["join and speak", { botCanJoin: false, botCanSpeak: false }],
	])("rejects when the bot lacks %s permission", (_, overrides) => {
		expect(
			evaluateGuardPolicy("new-or-existing-session", undefined, {
				...ctx,
				voiceChannel: { ...voiceChannel, ...overrides },
			}),
		).toEqual(err("not-enough-permissions"));
	});

	it("rejects a caller outside any voice channel", () => {
		expect(
			evaluateGuardPolicy("new-or-existing-session", undefined, {
				...ctx,
				voiceChannel: undefined,
			}),
		).toEqual(err("user-not-in-voice-channel"));
	});
});
