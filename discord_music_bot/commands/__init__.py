import logging

import discord

from discord_music_bot.commands.audio import AudioCommands
from discord_music_bot.commands.queue import QueueCommands
from discord_music_bot.commands.streaming import StreamingCommands


def add_cogs(bot: discord.Bot) -> None:
    logger = logging.getLogger("discord_music_bot")

    bot.add_cog(AudioCommands(bot=bot, logger=logger))
    bot.add_cog(QueueCommands(bot=bot, logger=logger))
    bot.add_cog(StreamingCommands(bot=bot, logger=logger))
