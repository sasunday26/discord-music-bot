from datetime import timedelta

import discord
import wavelink


def format_timedelta(delta: timedelta) -> str:
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (f"{hours}" if hours > 0 else "") + f"{minutes}:{seconds:02d}"


async def get_current_player(
    ctx: discord.ApplicationContext,
) -> wavelink.Player:
    player: wavelink.Player = ctx.voice_client

    if not player:
        await ctx.respond("Not connected to a voice channel")
        raise discord.ClientException("Bot is not in a voice channel")

    return player
