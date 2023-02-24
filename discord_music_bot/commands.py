from typing import cast

import discord
import yt_dlp  # type: ignore
from discord.ext import commands

from discord_music_bot import compat, config


class StreamingCommands(
    discord.Cog,
    guild_ids=config.GUILD_IDS,
):
    @discord.slash_command(
        name="yt",
        description="play audio from a YouTube video",
    )
    async def youtube(self, ctx: compat.ApplicationContext, url: str) -> None:
        with yt_dlp.YoutubeDL(config.YDL_OPTIONS) as ytdl:
            data = cast(dict, ytdl.extract_info(url, download=False))

            if entries := data.get("entries"):
                data = entries[0]

            player = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(data["url"], **config.FFMPEG_OPTIONS)
            )
            ctx.voice_client.play(
                player, after=lambda e: print(e) if e else None
            )

            await ctx.respond(f"Now playing: {data['title']}")

    @youtube.before_invoke
    async def connect_to_current_voice(
        self, ctx: compat.ApplicationContext
    ) -> None:
        channel = await self.get_current_voice_channel(ctx)

        # bot is not in a voice channel
        if not ctx.voice_client:
            await channel.connect()
            await ctx.respond(f"Connecting to {channel.name}")
            return

        # bot is in the same voice channel already
        if ctx.voice_client.channel == channel:
            ctx.voice_client.stop()
            return

        # bot is playing in a different voice channel
        if ctx.voice_client.is_playing():
            await ctx.respond("Sorry, I'm busy")
            raise commands.CommandError("Bot is busy in a different channel")

        # await ctx.voice_client.move_to(channel)

    @discord.slash_command()
    async def volume(
        self, ctx: compat.ApplicationContext, volume: int
    ) -> None:
        if ctx.voice_client is None:
            await ctx.respond("Not in a voice channel")
            return

        if not 0 <= volume <= 200:
            await ctx.respond("Volume must be in range 0-200")
            return

        if ctx.voice_client.source is None:
            return

        ctx.voice_client.source.volume = volume / 100
        await ctx.respond(f"Volume set to {volume}%")

    @discord.slash_command()
    async def pause(self, ctx: compat.ApplicationContext) -> None:
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.respond("Pausing...")

    @discord.slash_command()
    async def resume(self, ctx: compat.ApplicationContext) -> None:
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.respond("Resuming...")

    @discord.slash_command(name="shut_the_fuck_up")
    async def leave(self, ctx: compat.ApplicationContext) -> None:
        if ctx.voice_client:
            await ctx.respond("Leaving...")
            await ctx.voice_client.disconnect(force=False)
            return

        await ctx.respond("Not in a voice channel")

    @volume.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @leave.before_invoke
    async def user_is_in_current_voice_channel(
        self, ctx: compat.ApplicationContext
    ) -> None:
        channel = await self.get_current_voice_channel(ctx)

        # bot is not in a voice channel
        if not ctx.voice_client:
            await ctx.respond("Bot is not in a voice channel")
            raise commands.CommandError("Bot is not in a voice channel")

        # bot is in a different voice channel
        if ctx.voice_client.channel != channel:
            await ctx.respond("You're in a different voice channel")
            raise commands.CommandError("User is in a different voice channel")

    async def get_current_voice_channel(
        self, ctx: compat.ApplicationContext
    ) -> discord.VoiceChannel:
        author = cast(discord.Member, ctx.author)
        voice_state = author.voice

        if not voice_state:
            await ctx.respond("You're not in a voice channel")
            raise commands.CommandError("User is not in a voice channel")

        return cast(discord.VoiceChannel, voice_state.channel)


def add_cogs(bot: discord.Bot) -> None:
    bot.add_cog(StreamingCommands())
