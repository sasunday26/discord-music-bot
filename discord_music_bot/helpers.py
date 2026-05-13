from datetime import timedelta

import discord
import lavalink


def format_timedelta(delta: timedelta) -> str:
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (
        f"{hours:02d}:" if hours > 0 else ""
    ) + f"{minutes:02d}:{seconds:02d}"


async def get_current_player(
    interaction: discord.Interaction,
) -> lavalink.DefaultPlayer:
    guild = interaction.guild

    if not guild:
        raise discord.DiscordException("interaction.guild is None")

    player = interaction.client.lavalink.player_manager.get(guild.id)

    if not player or not player.is_connected:
        await interaction.response.send_message(
            "You're not in a voice channel"
        )
        raise discord.DiscordException(
            "interaction.guild.voice_client is None"
        )

    return player
