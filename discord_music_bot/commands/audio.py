import re
from datetime import timedelta

import discord
import wavelink

from discord_music_bot.commands.base import BaseCog
from discord_music_bot.helpers import format_timedelta, get_current_player


class AudioCommands(BaseCog):
    @discord.slash_command(
        name="pause", description="pause the currently playing song"
    )
    async def pause(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if not player.is_playing():
            await ctx.respond("Not playing")
            return

        await player.pause()
        await ctx.respond("Paused playback")

    @discord.slash_command(
        name="resume", description="resume playing the currently paused song"
    )
    async def resume(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        if not player.is_paused():
            await ctx.respond("Not paused")
            return

        await player.resume()
        await ctx.respond("Resuming playback")

    @discord.slash_command(
        name="shut_the_fuck_up", description="SHUT THE FUCK UP"
    )
    async def leave(self, ctx: discord.ApplicationContext) -> None:
        player = await get_current_player(ctx)

        await player.disconnect()
        await ctx.respond("Ok")

    @discord.slash_command(name="volume", description="set audio volume")
    @discord.option(
        "volume",
        int,
        min_value=0,
        max_value=1000,
        description="percentage from 0 to 1000",
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
        name="seek", description="seek to a specified position"
    )
    @discord.option(
        "position", str, description="timestamp (4:20) or seconds (260)"
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

    @discord.slash_command(
        name="equalizer",
        description="add equalizer filter",
    )
    @discord.option(
        "settings",
        description=(
            "band:gain separated by space: 1:0.75 2:0.8 3:0.5 "
            "band range: 0-15, gain range: -0.25-1.0"
        ),
    )
    async def add_equalizer(
        self, ctx: discord.ApplicationContext, *, settings: str
    ) -> None:
        player = await get_current_player(ctx)

        # bands is list of tuples that contain band number and its gain,
        # where band is a frequency and gain is its amplification factor.
        # the lower the band number, the lower the frequency

        # for example: [(1, 0.75), (2, 0.8), (3, 0.5)]
        # in this example, three low frequency bands are amplified
        bands: list[tuple[int, float]] = []
        for param in settings.strip().split(" "):
            if not param:
                continue

            band, gain = param.split(":")
            bands.append((int(band), float(gain)))

        try:
            await player.set_filter(
                wavelink.Filter(equalizer=wavelink.Equalizer(bands=bands)),
                seek=True,
            )
        except ValueError:
            await ctx.respond("Invalid value")
            return

        await ctx.respond("Equalizer added")

    @discord.slash_command(name="speed", description="set playback speed")
    @discord.option(
        "speed", float, min_value=0.0, description="playback speed multiplier"
    )
    @discord.option(
        "pitch",
        float,
        default=1.0,
        min_value=0.0,
        description="track pitch multiplier",
    )
    async def set_speed(
        self, ctx: discord.ApplicationContext, *, speed: float, pitch: float
    ) -> None:
        player = await get_current_player(ctx)

        await player.set_filter(
            wavelink.Filter(
                timescale=wavelink.Timescale(speed=speed, pitch=pitch)
            ),
            seek=True,
        )

        await ctx.respond("New speed applied")
