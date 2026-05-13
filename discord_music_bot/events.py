import asyncio
import logging
import discord
import lavalink

from . import config
from .client import CustomClient

def add_client_events(client: CustomClient, logger: logging.Logger) -> None:
    async def lavalink_hook(event: lavalink.events.Event):
        if isinstance(event, lavalink.events.TrackStartEvent):
            player = event.player
            track = event.track

            embed: discord.Embed = discord.Embed(
                title="Now Playing", colour=discord.Colour.random()
            )
            embed.description = f"**{track.title}** by `{track.author}`"

            if track.artwork_url:
                embed.set_image(url=track.artwork_url)

            # autoplay is handled differently now

            await client.change_presence(
                activity=discord.Activity(
                    name=f"{track.title} - {track.author}",
                    type=discord.ActivityType.listening,
                ),
                status=discord.Status.online,
            )

            channel_id = player.fetch("channel_id")
            if channel_id:
                channel = client.get_channel(int(channel_id))
                if channel:
                    await channel.send(embed=embed)

        elif isinstance(event, lavalink.events.TrackEndEvent):
            logger.info(
                f"track {event.track.title} finished playing, "
                f"because {event.reason}"
            )
            
            player = event.player

            # When the last track finishes, reset status
            if not player.queue and event.reason in ("finished", "stopped", "loadFailed", "FINISHED", "STOPPED", "LOAD_FAILED"):
                await client.change_presence(activity=None, status=discord.Status.idle)
                

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
        if not hasattr(client, 'lavalink_hooks_added') or not client.lavalink_hooks_added:
            client.lavalink.add_event_hook(lavalink_hook)
            client.lavalink_hooks_added = True

    def is_alone_in_voice_channel(channel: discord.VoiceChannel) -> bool:
        return len(channel.members) == 1

    @client.event
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if not hasattr(client, 'lavalink'):
            return

        for player in client.lavalink.player_manager.values():
            if not player.is_connected:
                continue
                
            trigger_channel = client.get_channel(int(player.channel_id))

            if not (
                isinstance(trigger_channel, discord.VoiceChannel)
                and is_alone_in_voice_channel(trigger_channel)
            ):
                continue

            async def delayed_leave(p, chan_id):
                await asyncio.sleep(config.LEAVE_AFTER)

                current_channel = client.get_channel(chan_id.id)
                current_is_alone = is_alone_in_voice_channel(current_channel) if isinstance(current_channel, discord.VoiceChannel) else False

                if not (
                    isinstance(current_channel, discord.VoiceChannel)
                    and current_is_alone
                    and p.is_connected
                ):
                    return

                guild = client.get_guild(int(p.guild_id))
                if guild and guild.voice_client:
                    await guild.voice_client.disconnect(force=False)
                else:
                    await p.stop()

                text_channel_id = p.fetch("channel_id")
                if text_channel_id:
                    text_channel = client.get_channel(int(text_channel_id))
                    if text_channel:
                        await text_channel.send("No one in the voice channel. Leaving...")

                await client.change_presence(activity=None, status=discord.Status.idle)

            asyncio.create_task(delayed_leave(player, trigger_channel))

