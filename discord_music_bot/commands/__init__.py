import logging

import discord

from discord_music_bot.commands.streaming import StreamingCommands


def add_cogs(bot: discord.Bot) -> None:
    logger = logging.getLogger("discord_music_bot")

    bot.add_cog(StreamingCommands(bot, logger))
