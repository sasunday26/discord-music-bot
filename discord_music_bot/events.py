import asyncio
import logging

import discord
import wavelink
from wavelink import QueueMode, AutoPlayMode

from . import config
from .client import CustomClient


def add_client_events(client: CustomClient, logger: logging.Logger) -> None:
    @client.event
    async def on_wavelink_track_start(
        payload: wavelink.TrackStartEventPayload,
    ) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        if player.queue.mode == QueueMode.loop:
            if not hasattr(player, "last_track"):
                player.last_track = track
            elif player.last_track == track:
                return

        embed: discord.Embed = discord.Embed(
            title="Now Playing", colour=discord.Colour.random()
        )
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += (
                f"\n\n`This track was recommended via {track.source}`"
            )

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        await player.home.send(embed=embed)

        await client.change_presence(
            activity=discord.Activity(
                name=f'{"(AP) " if original and original.recommended else ""}'
                + f"{payload.track.title} - {payload.track.author}",
                type=discord.ActivityType.listening,
            ),
            status=discord.Status.online,
        )

    @client.event
    async def on_wavelink_track_end(
        payload: wavelink.TrackEndEventPayload,
    ) -> None:
        logger.info(
            f"track {payload.track} finished playing, "
            f"because {payload.reason}"
        )

        if (
            payload.player.queue.mode == QueueMode.loop
            and payload.reason == "finished"
        ):
            await payload.player.play(payload.track)
            return

        if (
            payload.player.queue.is_empty
            and payload.player.autoplay == AutoPlayMode.disabled
        ):
            await client.change_presence(status=discord.Status.idle)
            return

        if payload.reason == "replaced":
            return

        if payload.reason == "stopped" and hasattr(
            payload.player, "last_track"
        ):
            delattr(payload.player, "last_track")

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

    @client.event
    async def on_ready():
        await client.tree.sync()

    @client.event
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        for player in client.voice_clients:
            if (
                before.channel
                and len(before.channel.members) == 1
                and not after.channel
            ):
                if player.channel == before.channel:
                    await asyncio.sleep(config.LEAVE_AFTER)

                    if isinstance(player.channel, discord.VoiceChannel):
                        channel = await client.fetch_channel(player.channel.id)
                        if (
                            isinstance(channel, discord.VoiceChannel)
                            and len(channel.members) == 1
                            and player in client.voice_clients
                        ):
                            await player.disconnect(force=False)

                            if hasattr(player, "home"):
                                await player.home.send(
                                    "No one in the voice channel. Leaving..."
                                )
                            await client.change_presence(
                                status=discord.Status.idle
                            )