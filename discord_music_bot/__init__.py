import logging
from logging.config import dictConfig

import discord

from discord_music_bot import config
from discord_music_bot.commands import add_cogs
from discord_music_bot.errors import add_error_handlers


def run_bot() -> None:
    dictConfig(config.LOGGING_CONFIG)
    logger = logging.getLogger("discord_music_bot")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Bot(
        intents=intents,
        command_prefix=config.COMMAND_PREFIX,
    )

    add_cogs(bot, logger)
    add_error_handlers(bot, logger)

    bot.run(config.BOT_TOKEN)
