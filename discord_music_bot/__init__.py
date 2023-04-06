import logging
from logging.config import dictConfig

from discord_music_bot.events import add_client_events

from . import config
from .client import CustomClient
from .commands import add_commands


def run_bot() -> None:
    dictConfig(config.LOGGING_CONFIG)
    logger = logging.getLogger("discord_music_bot")

    client = CustomClient()

    add_commands(client)
    add_client_events(client, logger)

    client.run(config.BOT_TOKEN)
