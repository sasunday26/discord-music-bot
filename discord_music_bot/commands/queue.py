from datetime import timedelta

import discord

from discord_music_bot.commands.base import BaseCog
from discord_music_bot.helpers import format_timedelta, get_current_player


class QueueCommands(BaseCog):
    @discord.slash_command(
        name="now_playing",
        description="get information about the currently playing song",
    )
    async def get_now_playing(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if not player.track:
            await ctx.respond("Not playing anything right now")
            return

        track = player.track

        embed = discord.Embed(
            title=track.title, colour=discord.Colour.random()
        )

        if track.author:
            embed.add_field(name="Author", value=track.author)

        position = timedelta(seconds=player.position)
        embed.add_field(name="Position", value=format_timedelta(position))

        duration = timedelta(seconds=track.length)
        embed.add_field(name="Duration", value=format_timedelta(duration))

        if track.uri:
            embed.add_field(name="Link", value=track.uri)

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="queue", description="get list of tracks in the queue"
    )
    async def get_queue(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if player.queue.is_empty:
            await ctx.respond("Queue is empty")
            return

        embed = discord.Embed(
            title="Songs in queue:", colour=discord.Colour.random()
        )

        for i, track in enumerate(player.queue, start=1):
            embed.add_field(name=f"**{track.title}**", value=str(i))

        await ctx.respond(embed=embed)

    @discord.slash_command(name="clear", description="clear the queue")
    async def clear_queue(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        player.queue.clear()
        await ctx.respond("Queue cleared")

    @discord.slash_command(
        name="skip", description="skip currently playing song"
    )
    async def play_next(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)
        skipped_item_title = player.track.title

        if player.queue.is_empty:
            await player.stop()
            await ctx.respond(
                f"Skipping **{skipped_item_title}**"
                "\nThis was the last one in queue"
            )
        else:
            current_item = player.queue.get()

            await player.play(current_item)
            await ctx.respond(
                f"Skipping **{skipped_item_title}**"
                f"\nPlaying **{current_item.title}**"
            )
