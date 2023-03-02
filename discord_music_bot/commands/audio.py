import re
from datetime import timedelta

import discord

from discord_music_bot.commands.base import BaseCog
from discord_music_bot.helpers import format_timedelta, get_current_player


class AudioCommands(BaseCog):
    @discord.slash_command(
        name="pause",
        description="pause the currently playing song",
    )
    async def pause(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if not player.is_playing():
            await ctx.respond("Not playing")
            return

        await player.pause()
        await ctx.respond("Paused playback")

    @discord.slash_command(
        name="resume",
        description="resume playing the currently paused song",
    )
    async def resume(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if not player.is_paused():
            await ctx.respond("Not paused")
            return

        await player.resume()
        await ctx.respond("Resuming playback")

    @discord.slash_command(
        name="shut_the_fuck_up", description="disconnect the bot"
    )
    async def leave(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        await player.disconnect()
        await ctx.respond("Ok")

    @discord.slash_command(
        name="volume",
        description="set the volume in the range 0-1000",
    )
    async def set_volume(
        self, ctx: discord.ApplicationContext, *, volume: int
    ) -> None:
        player = await get_current_player(ctx)

        if not 0 <= volume <= 1000:
            await ctx.respond("Volume must be in range 0-1000")
            return

        await player.set_volume(volume)
        await ctx.respond(f"Volume set to {volume}%")

    @discord.slash_command(
        name="seek",
        description="enter position in the song you want to skip to",
    )
    async def seek(
        self, ctx: discord.ApplicationContext, *, position: str
    ) -> None:
        player = await get_current_player(ctx)

        if not player.track:
            await ctx.respond("Not playing anything right now")
            return

        # matches \d+:\d+:\d+, \d+:\d+ and \d+
        # this allows entering position as a number of seconds.
        # for example, 300 will be treated as 5 minutes.
        matches = re.match(r"^(?:(?:(\d+):)?(\d+):)?(\d+)$", position)

        if not matches:
            await ctx.respond("Invalid position format")
            return

        hours, minutes, seconds = (
            int(m) if m else 0 for m in matches.groups()
        )
        position_td = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        duration = timedelta(seconds=player.track.length)
        if duration < position_td:
            await ctx.respond(
                "Track's total length is "
                f"{format_timedelta(duration)}, that is too far"
            )
            return

        await player.seek(position_td.total_seconds() * 1000)
        await ctx.respond(f"Seeking to {format_timedelta(position_td)}")
