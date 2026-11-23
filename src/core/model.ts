type CommandCtx = {
  readonly interactionId: string;
  readonly guildId: string;
  readonly channelId: string;
  readonly voiceChannelId: string | undefined;
  readonly botCanJoinVoice: boolean;
  readonly botCanSpeakVoice: boolean;
  readonly nowMs: number;
};

type LoadResult =
  | {
      readonly kind: "track";
      readonly track: Track;
    }
  | {
      readonly kind: "playlist";
      readonly tracks: readonly [Track, ...Track[]];
      readonly playlistName: string;
    }
  | {
      readonly kind: "search";
      readonly tracks: readonly [Track, ...Track[]];
    }
  | {
      readonly kind: "empty";
    }
  | { readonly kind: "error" };

const COMMAND_NAMES = [
  "play", // user connected & (bot can join | (bot connected & same voice))
  "pause", // user connected & bot connected & same voice
  "resume", // same as pause
  "skip", // same as pause
  "shut_the_fuck_up", // same as pause
  "seek", // same as pause
  "now_playing", // same as pause
  "queue", // same as pause
  "clear", // same as pause
  "volume", //same as pause
  "equalizer", //same as pause
  "speed", // same as pause
  "slowreverb", //same as pause
  "reset_filters", // same as pause
  "outro", // same as pause
] as const;
type CommandName = (typeof COMMAND_NAMES)[number];

const TRACK_END_REASONS = [
  "finished",
  "loadFailed",
  "stopped",
  "replaced",
  "cleanup",
] as const;
type TrackEndReason = (typeof TRACK_END_REASONS)[number];

type Event =
  | {
      readonly kind: "cmd/invoked";
      readonly name: CommandName;
      readonly ctx: CommandCtx;
      readonly rawArgs: Readonly<Record<string, unknown>>;
    }
  | {
      readonly kind: "lavalink/tracks-loaded";
      readonly guildId: string;
      readonly purpose: "play" | "outro";
      readonly ctx: CommandCtx;
      readonly result: LoadResult;
      readonly nowMs: number;
    }
  | {
      readonly kind: "lavalink/track-started";
      readonly guildId: string;
      readonly track: Track;
      readonly nowMs: number;
    }
  | {
      readonly kind: "lavalink/track-ended";
      readonly guildId: string;
      readonly reason: TrackEndReason;
      readonly nowMs: number;
    }
  | {
      readonly kind: "lavalink/player-updated";
      readonly guildId: string;
      readonly positionMs: number;
      readonly nowMs: number;
    }
  | { readonly kind: "lavalink/player-closed"; readonly guildId: string }
  | {
      readonly kind: "discord/voice-state-changed";
      readonly guildId: string;
      readonly voiceChannelId: string | undefined;
      readonly humanCount: number;
      readonly nowMs: number;
    }
  | {
      readonly kind: "timer/empty-vc-elapsed";
      readonly guildId: string;
      readonly humanCount: number;
    }
  | { readonly kind: "timer/outro-triggered"; readonly guildId: string };

const TIMER_KINDS = ["empty-vc", "outro"] as const;
type TimerKind = (typeof TIMER_KINDS)[number];

type EmbedField = {
  readonly inline: boolean;
  readonly name: string;
  readonly value: string;
};

type EmbedData = {
  // TODO: add all fields
  readonly author?: string;
  readonly color?: number;
  readonly description?: string;
  readonly fields?: readonly EmbedField[];
  readonly image?: {
    readonly url: string;
  };
  readonly thumbnail?: {
    readonly url: string;
  };
  readonly timestamp?: number;
  readonly title?: string;
  readonly url?: string;
};

type PresenceData =
  | { readonly kind: "idle" }
  | {
      readonly kind: "playing";
      readonly title: string;
      readonly author: string;
    };

type Effect = HandlerEffect | ReconcileEffect;

// Edge-triggered effects (emitted by handlers)
type HandlerEffect =
  | { readonly kind: "fx/defer-reply"; readonly interactionId: string }
  | {
      readonly kind: "fx/reply";
      readonly interactionId: string;
      readonly content: string;
      readonly ephemeral?: boolean;
    }
  | {
      readonly kind: "fx/reply";
      readonly interactionId: string;
      readonly embed: EmbedData;
      readonly ephemeral?: boolean;
    }
  | {
      readonly kind: "fx/send-channel";
      readonly channelId: string;
      readonly content: string;
    }
  | {
      readonly kind: "fx/send-channel";
      readonly channelId: string;
      readonly embed: EmbedData;
    }
  | {
      readonly kind: "fx/load-tracks";
      readonly guildId: string;
      readonly identifier: string;
      readonly purpose: "play" | "outro";
      readonly ctx: CommandCtx;
    }
  | {
      readonly kind: "fx/join-voice";
      readonly guildId: string;
      readonly voiceChannelId: string;
    }
  | { readonly kind: "fx/leave-voice"; readonly guildId: string }
  | {
      readonly kind: "fx/play-track";
      readonly guildId: string;
      readonly track: Track;
      readonly volume: number;
      readonly filters: FilterState;
    }
  | { readonly kind: "fx/stop-track"; readonly guildId: string }
  | {
      readonly kind: "fx/set-paused";
      readonly guildId: string;
      readonly paused: boolean;
    }
  | {
      readonly kind: "fx/seek-track";
      readonly guildId: string;
      readonly positionMs: number;
    }
  | {
      readonly kind: "fx/update-player";
      readonly guildId: string;
      readonly filters: FilterState;
    }
  | {
      readonly kind: "fx/update-player";
      readonly guildId: string;
      readonly volume: number;
    }
  | {
      readonly kind: "fx/update-player";
      readonly guildId: string;
      readonly filters: FilterState;
      readonly volume: number;
    }
  | {
      readonly kind: "fx/kick-members";
      readonly guildId: string;
      readonly voiceChannelId: string;
    };

// Level-triggered reconciled effects (emitted solely by reconcile)
type ReconcileEffect =
  | { readonly kind: "fx/set-presence"; readonly presence: PresenceData }
  | {
      readonly kind: "fx/arm-timer";
      readonly guildId: string;
      readonly timerKind: TimerKind;
      readonly delayMs: number;
    }
  | {
      readonly kind: "fx/cancel-timer";
      readonly guildId: string;
      readonly timerKind: TimerKind;
    };

type Transition<E extends Effect = Effect> = {
  readonly state: BotState;
  readonly effects: readonly E[];
};

type PositionAnchor = {
  readonly baseMs: number;
  readonly observedAtMs: number;
  readonly rate: number;
};

type Track = {
  readonly encoded: string;
  readonly title: string;
  readonly author: string;
  readonly albumName?: string;
  readonly uri?: string;
  readonly artworkUrl?: string;
  readonly duration:
    | { readonly kind: "live" }
    | {
        readonly kind: "finite";
        readonly ms: number;
        readonly seekable: boolean;
      };
};

type PlaybackState =
  | { readonly status: "idle" }
  | {
      readonly status: "playing";
      readonly track: Track;
      readonly anchor: PositionAnchor;
      readonly startedAtMs: number;
    }
  | {
      readonly status: "paused";
      readonly track: Track;
      readonly anchor: PositionAnchor;
    }
  | {
      readonly status: "outro";
      readonly track: Track;
      readonly anchor: PositionAnchor;
      readonly triggerAtMs: number;
    };

type FilterState = {
  readonly equalizer: ReadonlyMap<number, number>;
  readonly timescale?: { readonly speed: number; readonly pitch: number };
  readonly pluginFilters?: {
    readonly echo?: { readonly echoLength: number; readonly decay: number };
    readonly "low-pass"?: {
      readonly cutoffFrequency: number;
      readonly boostFactor: number;
    };
  };
};

type GuildSession = {
  readonly guildId: string;
  readonly voiceChannelId: string;
  readonly homeChannelId: string;
  readonly state: PlaybackState;
  readonly queue: readonly Track[];
  readonly volume: number; // TODO: move to FilterState
  readonly filters: FilterState;
  readonly emptySinceMs: number | undefined;
};

type BotState = {
  readonly guilds: ReadonlyMap<string, GuildSession>;
};

export {
  type BotState,
  COMMAND_NAMES,
  type CommandCtx,
  type CommandName,
  type Effect,
  type EmbedData,
  type EmbedField,
  type Event,
  type FilterState,
  type GuildSession,
  type HandlerEffect,
  type LoadResult,
  type PlaybackState,
  type PositionAnchor,
  type PresenceData,
  type ReconcileEffect,
  TIMER_KINDS,
  type TimerKind,
  TRACK_END_REASONS,
  type Track,
  type TrackEndReason,
  type Transition,
};
