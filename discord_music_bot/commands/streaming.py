import discord
import validators
import wavelink
from wavelink.ext import spotify

from discord_music_bot import config
from discord_music_bot.commands.base import BaseCog


class StreamingCommands(BaseCog):
    async def setup(self) -> None:
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.bot,
            **config.WAVELINK_CONFIG,
            spotify_client=spotify.SpotifyClient(
                **config.SPOTIFY_CONFIG,
            ),
        )

    @discord.slash_command(
        name="youtube",
        description="play audio from a YouTube video",
    )
    @discord.option("query", str, description="search request or URL")
    async def queue_youtube(
        self, ctx: discord.ApplicationContext, *, query: str
    ) -> None:
        player: wavelink.Player = ctx.voice_client

        player.queue.put(
            await wavelink.YouTubeTrack.search(query=query, return_first=True)
        )

    @discord.slash_command(
        name="spotify",
        description="play spotify tracks, playlists and albums from a URL",
    )
    @discord.option(
        "url",
        str,
        description=(
            "spotify URL "
            "(https://open.spotify.com/track|album|playlist/...)"
        ),
    )
    async def queue_spotify(
        self, ctx: discord.ApplicationContext, *, url: str
    ) -> None:
        player: wavelink.Player = ctx.voice_client
        decoded = spotify.decode_url(url)

        if not validators.url(url) or decoded is None:
            await ctx.respond("Invalid URL provided")
            return

        search_type = decoded["type"]
        query = decoded["id"]

        if search_type in (
            spotify.SpotifySearchType.album,
            spotify.SpotifySearchType.playlist,
        ):
            await ctx.respond("Loading tracks into the queue")

            async for partial in spotify.SpotifyTrack.iterator(
                query=query, partial_tracks=True, type=search_type
            ):
                player.queue.put(partial)
                await ctx.send(f"**{partial.title}** added to queue")

            await ctx.send(
                f"Loading done. Items in queue: {len(player.queue)}"
            )

        elif search_type == spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(
                query=query, type=search_type, return_first=True
            )
            player.queue.put(track)
            await ctx.respond(f"**{track.title}** added to queue")

        else:
            self.logger.error(
                f"Couldn't play spotify track: "
                f"url={url}, search_type={search_type}, query={query}"
            )
            await ctx.respond("Something went wrong")

    @queue_youtube.before_invoke
    @queue_spotify.before_invoke
    async def ensure_voice_channel(
        self,
        ctx: discord.ApplicationContext,
    ) -> None:
        author_voice = ctx.author.voice
        if not author_voice:
            raise discord.ApplicationCommandError(
                "User isn't in voice channel"
            )

        if not ctx.voice_client:
            await author_voice.channel.connect(cls=wavelink.Player)
            return

        if author_voice.channel != ctx.voice_client.channel:
            raise discord.ApplicationCommandError(
                "User is in a different channel"
            )

    @queue_youtube.after_invoke
    @queue_spotify.after_invoke
    async def start_playing(self, ctx: discord.ApplicationContext) -> None:
        player: wavelink.Player = ctx.voice_client

        if player.is_playing() or player.queue.is_empty:
            return

        if next_item := player.queue.get():
            await player.play(next_item)
            await ctx.send(f"Playing **{next_item.title}**")

    @discord.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason: str
    ) -> None:
        self.logger.info(f"track {track} finished playing, because {reason}")

        if player.queue.is_empty:
            return

        if next_item := player.queue.get():
            await player.play(next_item)
