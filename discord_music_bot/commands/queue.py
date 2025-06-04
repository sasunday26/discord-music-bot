# mypy: disable-error-code=arg-type

import discord

from ..client import CustomClient
from ..helpers import get_current_player
from ..player_service import (
    clear_queue as clear_player_queue,
    now_playing_embed,
    queue_embed,
    skip_current,
    toggle_autoplay as toggle_autoplay_mode,
    toggle_loop,
)


def add_queue_commands(client: CustomClient) -> None:
    @client.tree.command(
        name="now_playing",
        description="get information about the currently playing song",
    )
    async def get_now_playing(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        track = player.current

        if not track:
            await interaction.response.send_message(
                "Not playing anything right now"
            )
            return

        embed = now_playing_embed(player)
        await interaction.response.send_message(embed=embed)

    @client.tree.command(
        name="queue", description="get list of tracks in the queue"
    )
    async def get_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if player.queue.is_empty:
            await interaction.response.send_message("Queue is empty")
            return

        embed = queue_embed(list(player.queue), "Songs in queue:")
        await interaction.response.send_message(embed=embed)

    @client.tree.command(
        name="queue_autoplay",
        description="get list of tracks in the autoplay queue",
    )
    async def get_autoplay_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if player.auto_queue.is_empty:
            await interaction.response.send_message("Autoplay queue is empty")
            return

        embed = queue_embed(list(player.auto_queue), "Songs in autoplay queue:")
        await interaction.response.send_message(embed=embed)

    @client.tree.command(name="clear", description="clear the queue")
    async def clear_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = await clear_player_queue(player)
        await interaction.response.send_message(message)

    @client.tree.command(
        name="skip", description="skip currently playing song"
    )
    async def play_next(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = await skip_current(player)
        await interaction.response.send_message(message)
        if not player.playing:
            await interaction.followup.send("Finished playing queue")

    @client.tree.command(name="loop", description="loop current track")
    async def loop_track(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = toggle_loop(player)
        await interaction.response.send_message(message)

    @client.tree.command(name="autoplay", description="toggle autoplay")
    async def toggle_autoplay(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = toggle_autoplay_mode(player)
        await interaction.response.send_message(message)
