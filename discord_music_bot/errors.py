import logging

import discord


def add_error_handlers(bot: discord.Bot, logger=logging.Logger) -> None:
    @bot.before_invoke
    async def log_context(ctx: discord.ApplicationContext) -> None:
        ctx_info = {
            "author": {"id": ctx.author.id, "name": ctx.author.name},
            "guild_id": ctx.guild_id,
            "interaction": ctx.interaction.data,
        }
        logger.info(f"Discord context data: {ctx_info}")

    @bot.event
    async def on_application_command_error(
        _: discord.ApplicationContext, error: discord.DiscordException
    ) -> None:
        logger.exception("Error caught: ", exc_info=error)
