import discord
from .helpers import get_current_player

class NowPlayingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="skip_track_button")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            player = await get_current_player(interaction)
        except Exception:
            # get_current_player already sends a response if player is not found
            return

        if not player.current:
            await interaction.response.send_message("Nothing to skip right now.", ephemeral=True)
            return

        skipped_title = player.current.title
        skipped_author = player.current.author
        
        await player.skip()

        await interaction.response.send_message(
            f"{interaction.user.mention} skipped **`{skipped_title} - {skipped_author}`**"
        )
