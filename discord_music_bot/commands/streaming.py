# mypy: disable-error-code=arg-type
import asyncio

import discord
import validators
import wavelink
from discord import app_commands
from wavelink.ext import spotify

from .. import config
from ..client import CustomClient


def add_streaming_commands(client: CustomClient) -> None:
    @client.tree.command(
        name="youtube",
        description="play audio from a YouTube video",
    )
    @app_commands.describe(query="search request or URL")
    async def queue_youtube(
        interaction: discord.Interaction, *, query: str
    ) -> None:
        player = await ensure_voice_channel(interaction)
        track = await wavelink.YouTubeTrack.search(query, return_first=True)

        await player.queue.put_wait(track)
        await interaction.response.send_message(f"**{track}** added to queue")

        await start_playing(interaction, player)

    @client.tree.command(
        name="spotify",
        description="play spotify tracks, playlists and albums from a URL",
    )
    @app_commands.describe(
        url=(
            "spotify URL "
            "(https://open.spotify.com/track|album|playlist/...)"
        )
    )
    async def queue_spotify(
        interaction: discord.Interaction, *, url: str
    ) -> None:
        player = await ensure_voice_channel(interaction)
        decoded = spotify.decode_url(url)

        if not validators.url(url) or decoded is None:
            await interaction.response.send_message("Invalid URL provided")
            return

        search_type = decoded["type"]
        query = decoded["id"]

        if search_type in (
            spotify.SpotifySearchType.album,
            spotify.SpotifySearchType.playlist,
        ):
            await interaction.response.send_message(
                "Loading tracks into the queue"
            )
            tracks = spotify.SpotifyTrack.iterator(
                query=query, type=search_type
            )

            if not player.is_playing():
                first_item = await anext(tracks)
                await player.play(first_item)
                await interaction.followup.send(
                    f"Playing **{first_item.title}**"
                )

            async for track in tracks:
                await player.queue.put_wait(track)
                await interaction.followup.send(
                    f"**{track.title}** added to queue"
                )

            await interaction.followup.send(
                f"Loading done. Items in queue: {len(player.queue)}"
            )

        elif search_type == spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(
                query=query, type=search_type
            )
            await player.queue.put_wait(track)
            await interaction.response.send_message(
                f"**{track.title}** added to queue"
            )

        await start_playing(interaction, player)

    @client.tree.command(name="outro", description="epic disconnect")
    async def play_n_leave(interaction: discord.Interaction) -> None:
        player = await ensure_voice_channel(interaction)
        await interaction.response.send_message("It's time to go to sleep")

        track = await wavelink.YouTubeTrack.search(
            config.OUTRO_VIDEO["url"], return_first=True
        )
        await player.play(track)

        while player.current == track and player.is_playing():
            await asyncio.sleep(0.5)

            if player.position >= config.OUTRO_VIDEO["timestamp_ms"]:
                await player.disconnect()
                await client.change_presence(status=discord.Status.idle)

    async def ensure_voice_channel(
        interaction: discord.Interaction,
    ) -> wavelink.Player:
        if not interaction.user:
            raise discord.DiscordException("interaction.user is None")

        if not isinstance(interaction.user, discord.Member):
            raise discord.DiscordException(
                "interaction.user is not a discord.Member object"
            )

        author_voice = interaction.user.voice

        if not author_voice:
            await interaction.response.send_message(
                "You're not in a voice channel"
            )
            raise discord.DiscordException("interaction.user.voice is None")

        if not interaction.guild:
            raise discord.DiscordException("interaction.guild is None")

        player: wavelink.Player = interaction.guild.voice_client

        if not player and author_voice.channel:
            player = await author_voice.channel.connect(cls=wavelink.Player)
            return player

        if author_voice.channel != player.channel:
            await interaction.response.send_message(
                "You're in a different channel"
            )
            raise discord.DiscordException(
                "user is in a different voice channel"
            )

        return player

    async def start_playing(
        interaction: discord.Interaction, player: wavelink.Player
    ) -> None:
        if player.is_playing() or player.queue.is_empty:
            return

        next_item = player.queue.get()

        await player.play(next_item)
        await interaction.followup.send(f"Playing **{next_item.title}**")
