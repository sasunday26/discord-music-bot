# mypy: disable-error-code=arg-type

from datetime import timedelta

import discord
from wavelink import QueueMode, AutoPlayMode

from ..client import CustomClient
from ..helpers import format_timedelta, get_current_player


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

        embed = discord.Embed(
            title=track.title, colour=discord.Colour.random()
        )

        if track.author:
            embed.add_field(name="Author", value=track.author)

        position = timedelta(seconds=player.position // 1000)
        embed.add_field(name="Position", value=format_timedelta(position))

        duration = timedelta(seconds=track.length // 1000)
        embed.add_field(name="Duration", value=format_timedelta(duration))

        if track.uri:
            embed.add_field(name="Link", value=track.uri)

        if track.artwork:
            embed.set_image(url=track.artwork)

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        await interaction.response.send_message(embed=embed)

    @client.tree.command(
        name="queue", description="get list of tracks in the queue"
    )
    async def get_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if player.queue.is_empty:
            await interaction.response.send_message("Queue is empty")
            return

        embed = discord.Embed(
            title="Songs in queue:", colour=discord.Colour.random()
        )

        for i, track in enumerate(player.queue, start=1):
            embed.add_field(
                name=f"`{track.title} - {track.author}`", value=str(i)
            )

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

        embed = discord.Embed(
            title="Songs in autoplay queue:", colour=discord.Colour.random()
        )

        for i, track in enumerate(player.auto_queue, start=1):
            embed.add_field(
                name=f"`{track.title} - {track.author}`", value=str(i)
            )

        await interaction.response.send_message(embed=embed)

    @client.tree.command(name="clear", description="clear the queue")
    async def clear_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        player.queue.clear()
        await interaction.response.send_message("Queue cleared")

    @client.tree.command(
        name="skip", description="skip currently playing song"
    )
    async def play_next(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        skipped_item = await player.skip()

        if not skipped_item:
            await interaction.response.send_message("Nothing to skip")
            return

        await interaction.response.send_message(
            f"Skipping **`{skipped_item.title} - {skipped_item.author}`**"
        )
        if not player.playing:
            await interaction.followup.send("Finished playing queue")

    @client.tree.command(name="loop", description="loop current track")
    async def loop_track(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        is_looped = player.queue.mode == QueueMode.normal

        player.queue.mode = QueueMode.loop if is_looped else QueueMode.normal

        await interaction.response.send_message(
            f"Current track is {'' if is_looped else 'un'}looped"
        )

    @client.tree.command(name="autoplay", description="toggle autoplay")
    async def toggle_autoplay(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        player.autoplay = (
            AutoPlayMode.enabled
            if player.autoplay == AutoPlayMode.disabled
            else AutoPlayMode.disabled
        )

        state = "" if player.autoplay != AutoPlayMode.disabled else "not "
        await interaction.response.send_message(f"Autoplay is {state}enabled")
