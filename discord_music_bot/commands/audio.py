import discord
import wavelink

from discord_music_bot.commands.base import BaseCog


class AudioCommands(BaseCog):
    @discord.slash_command(
        name="pause",
        description="pause the currently playing song",
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
        description="resume playing the currently paused song",
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
        name="shut_the_fuck_up", description="disconnect the bot"
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
        description="set the volume in the range 0-1000",
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
