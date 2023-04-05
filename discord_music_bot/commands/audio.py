import re
from datetime import timedelta

import discord
import wavelink
from discord import app_commands

from ..helpers import format_timedelta, get_current_player


def add_audio_commands(tree: app_commands.CommandTree):
    @tree.command(name="pause", description="pause the currently playing song")
    async def pause(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if not player.is_playing():
            await interaction.response.send_message("Not playing")
            return

        await player.pause()
        await interaction.response.send_message("Paused playback")

    @tree.command(
        name="resume", description="resume playing the currently paused song"
    )
    async def resume(interaction: discord.Interaction) -> None:
        player = await get_current_player(ctx)

        if not player.is_paused():
            await interaction.response.send_message("Not paused")
            return

        await player.resume()
        await interaction.response.send_message("Resuming playback")

    @tree.command(name="shut_the_fuck_up", description="SHUT THE FUCK UP")
    async def leave(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        await player.disconnect()
        await interaction.response.send_message("Ok")

    @tree.command(name="volume", description="set audio volume")
    # @discord.option(
    #     "volume",
    #     int,
    #     min_value=0,
    #     max_value=1000,
    #     description="percentage from 0 to 1000",
    # )
    async def set_volume(
        interaction: discord.Interaction, *, volume: int
    ) -> None:
        player = await get_current_player(ctx)

        if not 0 <= volume <= 1000:
            await interaction.response.send_message(
                "Volume must be in range 0-1000"
            )
            return

        await player.set_volume(volume)
        await interaction.response.send_message(f"Volume set to {volume}%")

    @tree.command(name="seek", description="seek to a specified position")
    # @discord.option(
    #     "position", str, description="timestamp (4:20) or seconds (260)"
    # )
    async def seek(interaction: discord.Interaction, *, position: str) -> None:
        player = await get_current_player(ctx)

        if not player.track:
            await interaction.response.send_message(
                "Not playing anything right now"
            )
            return

        # matches \d+:\d+:\d+, \d+:\d+ and \d+
        # this allows entering position as a number of seconds.
        # for example, 300 will be treated as 5 minutes.
        matches = re.match(r"^(?:(?:(\d+):)?(\d+):)?(\d+)$", position)

        if not matches:
            await interaction.response.send_message("Invalid position format")
            return

        hours, minutes, seconds = (
            int(m) if m else 0 for m in matches.groups()
        )
        position_td = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        duration = timedelta(seconds=player.track.length)
        if duration < position_td:
            await interaction.response.send_message(
                "Track's total length is "
                f"{format_timedelta(duration)}, that is too far"
            )
            return

        await player.seek(position_td.total_seconds() * 1000)
        await interaction.response.send_message(
            f"Seeking to {format_timedelta(position_td)}"
        )

    @tree.command(
        name="equalizer",
        description="add equalizer filter",
    )
    # @discord.option(
    #     "settings",
    #     description=(
    #         "band:gain separated by space: 1:0.75 2:0.8 3:0.5 "
    #         "band range: 0-15, gain range: -0.25-1.0"
    #     ),
    # )
    async def add_equalizer(
        interaction: discord.Interaction, *, settings: str
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
            await interaction.response.send_message("Invalid value")
            return

        await interaction.response.send_message("Equalizer added")

    @tree.command(name="speed", description="set playback speed")
    # @discord.option(
    #     "speed", float, min_value=0.0, description="playback speed multiplier"
    # )
    # @discord.option(
    #     "pitch",
    #     float,
    #     default=1.0,
    #     min_value=0.0,
    #     description="track pitch multiplier",
    # )
    async def set_speed(
        interaction: discord.Interaction, *, speed: float, pitch: float
    ) -> None:
        player = await get_current_player(ctx)

        await player.set_filter(
            wavelink.Filter(
                timescale=wavelink.Timescale(speed=speed, pitch=pitch)
            ),
            seek=True,
        )

        await interaction.response.send_message("New speed applied")
