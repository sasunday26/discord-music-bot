# mypy: disable-error-code=arg-type

import re
from datetime import timedelta

import discord
import wavelink
from discord import app_commands
from wavelink.types.filters import Equalizer

from ..client import CustomClient
from ..helpers import format_timedelta, get_current_player


def add_audio_commands(client: CustomClient) -> None:
    @client.tree.command(name="pause", description="pause/resume current song")
    async def pause(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        if not player.playing:
            await interaction.response.send_message("Not playing")
            return

        await player.pause(not player.paused)
        await interaction.response.send_message(
            "Paused" if player.paused else "Resumed"
        )

    @client.tree.command(
        name="shut_the_fuck_up", description="SHUT THE FUCK UP"
    )
    async def leave(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)

        await player.disconnect()
        await interaction.response.send_message("Ok")
        await client.change_presence(status=discord.Status.idle)

    @client.tree.command(name="volume", description="set audio volume")
    @app_commands.describe(volume="percentage from 0 to 1000")
    async def set_volume(
        interaction: discord.Interaction,
        *,
        volume: app_commands.Range[int, 0, 1000],
    ) -> None:
        player = await get_current_player(interaction)

        if not 0 <= volume <= 1000:
            await interaction.response.send_message(
                "Volume must be in range 0-1000"
            )
            return

        await player.set_volume(volume)
        await interaction.response.send_message(f"Volume set to {volume}%")

    @client.tree.command(
        name="seek", description="seek to a specified position"
    )
    @app_commands.describe(position="timestamp (4:20) or seconds (260)")
    async def seek(interaction: discord.Interaction, *, position: str) -> None:
        player = await get_current_player(interaction)

        if not player.current:
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

        duration = timedelta(seconds=player.current.length)
        if duration < position_td:
            await interaction.response.send_message(
                "Track's total length is "
                f"{format_timedelta(duration)}, that is too far"
            )
            return

        await player.seek(position_td.seconds * 1000)
        await interaction.response.send_message(
            f"Seeking to {format_timedelta(position_td)}"
        )

    @client.tree.command(
        name="equalizer",
        description="add equalizer filter",
    )
    @app_commands.describe(
        settings=(
            "band:gain separated by space: 1:0.75 2:0.8 3:0.5 "
            "band range: 0-15, gain range: -0.25-1.0"
        ),
    )
    async def add_equalizer(
        interaction: discord.Interaction, *, settings: str
    ) -> None:
        player = await get_current_player(interaction)

        # bands is list of tuples that contain band number and its gain,
        # where band is a frequency and gain is its amplification factor.
        # the lower the band number, the lower the frequency

        # for example: [(1, 0.75), (2, 0.8), (3, 0.5)]
        # in this example, three low frequency bands are amplified
        bands: list[Equalizer] = []
        for param in settings.strip().split(" "):
            if not param:
                continue

            band, gain = param.split(":")
            bands.append(Equalizer(band=int(band), gain=float(gain)))
        filters: wavelink.Filters = player.filters
        filters.equalizer.set(bands=bands)

        try:
            await player.set_filters(filters, seek=True)
        except ValueError:
            await interaction.response.send_message("Invalid value")
            return

        await interaction.response.send_message("Equalizer added")

    @client.tree.command(name="speed", description="set playback speed")
    @app_commands.describe(
        speed="playback speed multiplier", pitch="track pitch multiplier"
    )
    async def set_speed(
        interaction: discord.Interaction,
        *,
        speed: app_commands.Range[float, 0.0],
        pitch: app_commands.Range[float, 0.0] = 1.0,
    ) -> None:
        player = await get_current_player(interaction)

        filters: wavelink.Filters = player.filters
        filters.timescale.set(speed=speed, pitch=pitch)

        await player.set_filters(filters, seek=True)
        await interaction.response.send_message("New speed applied")
