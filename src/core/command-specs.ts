import type { CommandName } from "./model.ts";

type Guard =
  | {
      readonly kind: "new-session";
      readonly callerVoiceChannelId: string;
    }
  | {
      readonly kind: "existing-session";
      readonly session: string;
    };

type OptionSpec =
  | {
      readonly kind: "string";
      readonly name: string;
      readonly description: string;
      readonly required?: true;
    }
  | {
      readonly kind: "int" | "number";
      readonly name: string;
      readonly description: string;
      readonly required: true;
      readonly default?: number;
      readonly min?: number;
      readonly max?: number;
    }
  | {
      readonly kind: "int" | "number";
      readonly name: string;
      readonly description: string;
      readonly required?: true;
      readonly default: number;
      readonly min?: number;
      readonly max?: number;
    };

type CommandSpec = {
  readonly name: CommandName;
  readonly description: string;
  readonly guard: Guard;
  readonly options: readonly OptionSpec[];
};

const toDiscordCommandsJson = () => {};
const parseCommandArgs = () => {};
