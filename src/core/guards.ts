import type { CommandCtx, GuildSession } from "./model.ts";
import { err, ok, type Result } from "./result.ts";

type GuardPolicy = "existing-session" | "new-or-existing-session";

const evaluateGuardPolicy = (
	policy: GuardPolicy,
	session: GuildSession | undefined,
	ctx: CommandCtx,
): Result<GuardOutcome, GuardError> => {
	switch (policy) {
		case "existing-session":
			return guardExistingSession(session, ctx);

		case "new-or-existing-session":
			return guardNewOrExistingSession(session, ctx);
	}
};

type GuardOutcome =
	| {
			readonly kind: "new-session";
			readonly callerVoiceChannelId: string;
	  }
	| {
			readonly kind: "existing-session";
			readonly session: GuildSession;
	  };

const guardNewOrExistingSession = (
	session: GuildSession | undefined,
	ctx: CommandCtx,
): Result<GuardOutcome, GuardError> =>
	session === undefined
		? guardNewSession(ctx)
		: guardExistingSession(session, ctx);

const guardNewSession = (
	ctx: CommandCtx,
): Result<Extract<GuardOutcome, { kind: "new-session" }>, GuardError> =>
	requireBotCanUseVoiceChannel(ctx).andThen(() =>
		requireUserInVoiceChannel(ctx).map((i) => ({
			kind: "new-session",
			callerVoiceChannelId: i,
		})),
	);

const guardExistingSession = (
	session: GuildSession | undefined,
	ctx: CommandCtx,
): Result<Extract<GuardOutcome, { kind: "existing-session" }>, GuardError> => {
	const s = requireSession(session);
	if (s.isErr()) return err(s.error);

	const i = requireUserInVoiceChannel(ctx);
	if (i.isErr()) return err(i.error);

	const h = requireHomeChannel(s.value, ctx.channelId);
	if (h.isErr()) return err(h.error);

	const v = requireSameVoiceChannel(s.value, i.value);
	if (v.isErr()) return err(v.error);

	return ok({ kind: "existing-session", session: s.value });
};

type GuardError =
	| "no-active-session"
	| "not-enough-permissions"
	| "user-not-in-voice-channel"
	| "different-voice-channel"
	| "different-text-channel";

const requireSession = (
	session: GuildSession | undefined,
): Result<GuildSession, "no-active-session"> =>
	session === undefined ? err("no-active-session") : ok(session);

const requireUserInVoiceChannel = (
	ctx: Pick<CommandCtx, "voiceChannelId">,
): Result<string, "user-not-in-voice-channel"> =>
	ctx.voiceChannelId === undefined
		? err("user-not-in-voice-channel")
		: ok(ctx.voiceChannelId);

const requireBotCanUseVoiceChannel = (
	ctx: Pick<CommandCtx, "botCanJoinVoice" | "botCanSpeakVoice">,
): Result<void, "not-enough-permissions"> =>
	ctx.botCanJoinVoice && ctx.botCanSpeakVoice
		? ok(undefined)
		: err("not-enough-permissions");

const requireSameVoiceChannel = (
	session: GuildSession,
	voiceChannelId: string,
): Result<void, "different-voice-channel"> =>
	session.voiceChannelId === voiceChannelId
		? ok(undefined)
		: err("different-voice-channel");

const requireHomeChannel = (
	session: GuildSession,
	channelId: string,
): Result<void, "different-text-channel"> =>
	session.homeChannelId === channelId
		? ok(undefined)
		: err("different-text-channel");

export {
	evaluateGuardPolicy,
	type GuardError,
	type GuardOutcome,
	type GuardPolicy,
};
