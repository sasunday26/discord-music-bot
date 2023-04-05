from datetime import timedelta

import discord
import wavelink


def format_timedelta(delta: timedelta) -> str:
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (f"{hours}" if hours > 0 else "") + f"{minutes}:{seconds:02d}"


async def get_current_player(
    interaction: discord.Interaction,
) -> wavelink.Player:
    guild: discord.Guild = interaction.guild

    if not guild:
        await interaction.response.send_message(
            "No guild in interaction object"
        )
        raise discord.DiscordException("interaction.guild is None")

    player: wavelink.Player = guild.voice_client

    if not player:
        await interaction.response.send_message(
            "Not connected to a voice channel"
        )
        raise discord.DiscordException(
            "interaction.guild.voice_client is None"
        )

    return player
