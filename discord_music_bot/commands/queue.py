# mypy: disable-error-code=arg-type

from datetime import timedelta

import discord

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
            embed.add_field(name=f"**{track.title}**", value=str(i))

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
        skipped_item = player.current

        if not skipped_item:
            await interaction.response.send_message("Nothing to skip")
            return

        if player.queue.is_empty:
            await player.stop()
            await interaction.response.send_message(
                f"Skipping **{skipped_item.title}**"
            )
            await interaction.followup.send("This was the last one in queue")
            await client.change_presence(status=discord.Status.idle)
            return

        current_item = player.queue.get()

        await player.play(current_item)
        await interaction.response.send_message(
            f"Skipping **{skipped_item.title}**"
        )
        await interaction.followup.send(f"Playing **{current_item.title}**")

    @client.tree.command(name="loop", description="loop current track")
    async def loop_track(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        is_looped = not player.queue.loop
        player.queue.loop = is_looped

        if is_looped and (current := player.current):
            player.queue.put_at_front(current)

        await interaction.response.send_message(
            f"Current track is {'' if is_looped else 'un'}looped"
        )
