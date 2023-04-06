import logging

import discord
import wavelink

from .client import CustomClient


def add_client_events(client: CustomClient, logger=logging.Logger) -> None:
    @client.event
    async def on_wavelink_track_end(
        payload: wavelink.TrackEventPayload,
    ) -> None:
        logger.info(
            f"track {payload.track} finished playing, "
            f"because {payload.reason}"
        )

        if payload.player.queue.is_empty or payload.reason == "REPLACED":
            return

        await payload.player.play(payload.player.queue.get())

    @client.event
    async def on_message(message: discord.Message) -> None:
        message_info = {
            "author": {"id": message.author.id, "name": message.author.name},
            "guild_id": (
                {"id": message.guild.id, "name": message.guild.name}
                if message.guild
                else None
            ),
            "content": message.content,
        }
        logger.info(f"{message_info=}")

    @client.event
    async def on_error(event: str, *args, **kwargs) -> None:
        logger.error(f"{event=}, {args=}, {kwargs=}")
