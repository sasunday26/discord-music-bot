import { type GuildSession } from "./model.ts";

const requireSession = (session: GuildSession | undefined): boolean => {};
const requireUserInVoice = (session: GuildSession): boolean => {};
const requireSameVoice = (session: GuildSession): boolean => {};
const requireHomeChannel = (session: GuildSession): boolean => {};
