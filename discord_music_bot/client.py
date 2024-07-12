import discord
import wavelink
from discord import app_commands

from . import config


class CustomClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        node = wavelink.Node(**config.WAVELINK_CONFIG)

        await wavelink.Pool.connect(
            client=self, nodes=[node], cache_capacity=None
        )
