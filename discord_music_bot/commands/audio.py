import logging

import discord
import wavelink

from discord_music_bot import config


class AudioCommands(
    discord.Cog,
    guild_ids=config.GUILD_IDS,
):
    def __init__(
        self,
        bot: discord.Bot,
        logger: logging.Logger,
    ) -> None:
        self.bot = bot
        self.logger = logger

    @discord.slash_command(
        name="pause",
        description="pause currently playing song, if any",
    )
    async def pause(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

        if not player.is_playing():
            await ctx.respond("Not playing")
            return

        await player.pause()
        await ctx.respond("Paused playback")

    @discord.slash_command(
        name="resume",
        description="resume playing currently paused song, if any",
    )
    async def resume(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

        if not player.is_paused():
            await ctx.respond("Not paused")
            return

        await player.resume()
        await ctx.respond("Resuming playback")

    @discord.slash_command(
        name="shut_the_fuck_up", description="disconnect bot"
    )
    async def leave(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

        await player.disconnect()
        await ctx.respond("Ok")

    @discord.slash_command(
        name="volume",
        description="set playback volume in range 0-1000",
    )
    async def set_volume(
        self, ctx: discord.ApplicationContext, *, volume: int
    ) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            await ctx.respond("Not connected to a voice channel")
            return

        if not 0 <= volume <= 1000:
            await ctx.respond("Volume must be in range 0-1000")
            return

        await player.set_volume(volume)
        await ctx.respond(f"Volume set to {volume}%")
