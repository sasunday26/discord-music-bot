# mypy: disable-error-code=arg-type

from datetime import timedelta

import discord
import lavalink

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

        duration = timedelta(seconds=track.duration // 1000)
        embed.add_field(name="Duration", value=format_timedelta(duration))

        if track.uri:
            embed.add_field(name="Link", value=track.uri)

        if track.artwork_url:
            embed.set_image(url=track.artwork_url)

        await interaction.response.send_message(embed=embed)

    @client.tree.command(
        name="queue", description="get list of tracks in the queue"
    )
    async def get_queue(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if not player.queue:
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
        description="get list of tracks in the autoplay queue (NOT IMPLEMENTED IN LAVALINK)",
    )
    async def get_autoplay_queue(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Autoplay is not implemented natively in lavalink.")

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
        
        if not player.current:
             await interaction.response.send_message("Nothing to skip")
             return

        skipped_title = player.current.title
        skipped_author = player.current.author
        
        await player.skip()

        await interaction.response.send_message(
            f"Skipping **`{skipped_title} - {skipped_author}`**"
        )
        if not player.is_playing:
            await interaction.followup.send("Finished playing queue")

    @client.tree.command(name="loop", description="loop current track")
    async def loop_track(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        # Loop Queue vs Loop None vs Loop Single
        # We will loop single track
        is_looped = player.loop == lavalink.Loop.SINGLE if hasattr(lavalink, "Loop") else getattr(player, "loop", 0) == 1
        
        if not is_looped:
             player.set_loop(1) # SINGLE
             msg = "looped"
        else:
             player.set_loop(0) # NONE
             msg = "unlooped"

        await interaction.response.send_message(
            f"Current track is {msg}"
        )

    @client.tree.command(name="autoplay", description="toggle autoplay (NOT SUPPORTED)")
    async def toggle_autoplay(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Autoplay is currently not natively supported by lavalink.")
