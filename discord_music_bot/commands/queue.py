from datetime import timedelta

import discord
import wavelink

from discord_music_bot.commands.base import BaseCog


class QueueCommands(BaseCog):
    @discord.slash_command(
        name="now_playing",
        description="get information about the currently playing song",
    )
    async def get_now_playing(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player or not player.track:
            await ctx.respond("Not playing anything right now")
            return

        track = player.track

        embed = discord.Embed(
            title=track.title, colour=discord.Colour.random()
        )

        if track.author:
            embed.add_field(name="Author", value=track.author)

        embed.add_field(
            name="Duration", value=str(timedelta(seconds=track.length))
        )

        if track.uri:
            embed.add_field(name="Link", value=track.uri)

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="queue", description="get list of tracks in the queue"
    )
    async def get_queue(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

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
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

        player.queue.clear()
        await ctx.respond("Queue cleared")
