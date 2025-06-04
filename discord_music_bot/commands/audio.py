# mypy: disable-error-code=arg-type

import discord
from discord import app_commands

from ..client import CustomClient
from ..helpers import get_current_player
from ..player_service import (
    apply_equalizer_settings,
    disconnect_player,
    parse_equalizer,
    parse_timestamp,
    reset_player_filters,
    seek_player,
    set_playback_speed,
    set_player_volume,
    toggle_pause,
)


def add_audio_commands(client: CustomClient) -> None:
    @client.tree.command(name="pause", description="pause/resume current song")
    async def pause(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = await toggle_pause(player)
        await interaction.response.send_message(message)

    @client.tree.command(
        name="shut_the_fuck_up", description="SHUT THE FUCK UP"
    )
    async def leave(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = await disconnect_player(player, client)
        await interaction.response.send_message(message)

    @client.tree.command(name="volume", description="set audio volume")
    @app_commands.describe(volume="percentage from 0 to 1000")
    async def set_volume(
        interaction: discord.Interaction,
        *,
        volume: app_commands.Range[int, 0, 1000],
    ) -> None:
        if not 0 <= volume <= 1000:
            await interaction.response.send_message(
                "Volume must be in range 0-1000"
            )
            return
        player = await get_current_player(interaction)
        message = await set_player_volume(player, volume)
        await interaction.response.send_message(message)

    @client.tree.command(
        name="seek", description="seek to a specified position"
    )
    @app_commands.describe(position="timestamp (4:20) or seconds (260)")
    async def seek(interaction: discord.Interaction, *, position: str) -> None:
        player = await get_current_player(interaction)
        position_td = parse_timestamp(position)
        if not position_td:
            await interaction.response.send_message("Invalid position format")
            return

        message = await seek_player(player, position_td)
        await interaction.response.send_message(message)

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

        bands = parse_equalizer(settings)
        message = await apply_equalizer_settings(player, bands)
        await interaction.response.send_message(message)

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
        message = await set_playback_speed(player, speed, pitch)
        await interaction.response.send_message(message)

    @client.tree.command(
        name="reset_filters",
        description="reset all filters settings (equalizer, speed, volume )",
    )
    async def reset_filters(interaction: discord.Interaction) -> None:
        player = await get_current_player(interaction)
        message = await reset_player_filters(player)
        await interaction.response.send_message(message)
