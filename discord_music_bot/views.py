import discord
import wavelink
from datetime import timedelta

from typing import cast

from .helpers import format_timedelta, get_current_player
from .client import CustomClient


class ControlView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="10s Back",
        style=discord.ButtonStyle.secondary,
        custom_id="control_back_10",
        row=0,
    )
    async def back_ten(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)

        if not player.current:
            await interaction.response.send_message(
                "Not playing anything", ephemeral=True
            )
            return

        new_position = max(player.position - 10_000, 0)
        await player.seek(new_position)
        await interaction.response.send_message(
            "Seeking to "
            f"{format_timedelta(timedelta(milliseconds=new_position))}",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Pause/Resume",
        style=discord.ButtonStyle.primary,
        custom_id="control_pause",
        row=0,
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
        label="10s Forward",
        style=discord.ButtonStyle.secondary,
        custom_id="control_forward_10",
        row=0,
    )
    async def forward_ten(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)

        if not player.current:
            await interaction.response.send_message(
                "Not playing anything", ephemeral=True
            )
            return

        track = player.current
        new_position = min(
            player.position + 10_000,
            track.length,
        )
        await player.seek(new_position)
        await interaction.response.send_message(
            "Seeking to "
            f"{format_timedelta(timedelta(milliseconds=new_position))}",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Skip",
        style=discord.ButtonStyle.secondary,
        custom_id="control_skip",
        row=1,
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
        label="Loop",
        style=discord.ButtonStyle.secondary,
        custom_id="control_loop",
        row=1,
    )
    async def loop(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)
        is_looped = player.queue.mode == wavelink.QueueMode.normal

        player.queue.mode = (
            wavelink.QueueMode.loop if is_looped else wavelink.QueueMode.normal
        )

        await interaction.response.send_message(
            f"Current track is {'' if is_looped else 'un'}looped",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Shut the fuck up",
        style=discord.ButtonStyle.danger,
        custom_id="control_disconnect",
        row=1,
    )
    async def leave(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        player = await get_current_player(interaction)

        await player.disconnect()
        await interaction.response.send_message("Ok", ephemeral=True)
        client = cast(CustomClient, interaction.client)
        await client.change_presence(status=discord.Status.idle)
