import discord
import wavelink

from typing import cast

from .helpers import get_current_player
from .client import CustomClient


class ControlView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Pause/Resume",
        style=discord.ButtonStyle.primary,
        custom_id="control_pause",
    )
    async def pause(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)

        if not player.playing:
            await interaction.response.send_message(
                "Not playing", ephemeral=True
            )
            return

        await player.pause(not player.paused)
        await interaction.response.send_message(
            "Paused" if player.paused else "Resumed", ephemeral=True
        )

    @discord.ui.button(
        label="Skip",
        style=discord.ButtonStyle.secondary,
        custom_id="control_skip",
    )
    async def skip(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)
        skipped = await player.skip()

        if not skipped:
            await interaction.response.send_message(
                "Nothing to skip", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Skipping **`{skipped.title} - {skipped.author}`**",
            ephemeral=True,
        )
        if not player.playing:
            await interaction.followup.send("Finished playing queue")

    @discord.ui.button(
        label="Disconnect",
        style=discord.ButtonStyle.danger,
        custom_id="control_disconnect",
    )
    async def leave(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)

        await player.disconnect()
        await interaction.response.send_message("Ok", ephemeral=True)
        client = cast(CustomClient, interaction.client)
        await client.change_presence(status=discord.Status.idle)
