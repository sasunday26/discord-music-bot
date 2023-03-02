import logging

import discord

from discord_music_bot import config


class BaseCog(
    discord.Cog,
    guild_ids=config.GUILD_IDS,
):
    def __init__(
        self,
        bot: discord.Bot,
        logger: logging.Logger,
    ) -> None:
        self.bot = bot
        self.logger = logger

        bot.loop.create_task(self.setup())

    async def setup(self) -> None:
        ...
