import discord
import wavelink
from discord import app_commands
from wavelink.ext import spotify

from . import config


class CustomClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        for guild_id in config.GUILD_IDS:
            guild = discord.Object(guild_id)

            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        node = wavelink.Node(**config.WAVELINK_CONFIG)
        spotify_client = spotify.SpotifyClient(**config.SPOTIFY_CONFIG)

        await wavelink.NodePool.connect(
            client=self, nodes=[node], spotify=spotify_client
        )
