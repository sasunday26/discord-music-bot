import asyncio
from logging.config import dictConfig

import discord
from discord.ext import commands

from discord_music_bot import config
from discord_music_bot.commands import Commands


async def run_bot() -> None:
    dictConfig(config.LOGGING_CONFIG)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(
            config.DISCORD["COMMAND_PREFIX"]
        ),
        intents=intents,
    )

    async with bot:
        await bot.add_cog(Commands(bot))
        await bot.start(config.DISCORD["TOKEN"])


asyncio.run(run_bot())
