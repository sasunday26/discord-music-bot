# mypy: disable-error-code=arg-type
import discord

from ..client import CustomClient
from ..helpers import get_current_player
from ..views import ControlView


def add_control_commands(client: CustomClient) -> None:
    @client.tree.command(
        name="controls",
        description="show playback control buttons",
    )
    async def show_controls(interaction: discord.Interaction) -> None:
        await get_current_player(interaction)
        view = ControlView()
        await interaction.response.send_message(
            "Player controls:", view=view, ephemeral=True
        )
