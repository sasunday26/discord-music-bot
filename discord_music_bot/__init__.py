from logging.config import dictConfig

import discord

from discord_music_bot import config
from discord_music_bot.commands import add_cogs


def run_bot() -> None:
    dictConfig(config.LOGGING_CONFIG)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Bot(
        command_prefix=config.COMMAND_PREFIX,
        intents=intents,
    )

    add_cogs(bot)

    bot.run(config.BOT_TOKEN)
