# mypy: disable-error-code=arg-type
import asyncio

import discord
import wavelink
from discord import app_commands
from wavelink import TrackSource

from .. import config
from ..client import CustomClient


def add_streaming_commands(client: CustomClient) -> None:
    @client.tree.command(
        name="play",
        description="play video/track/playlist/stream "
        + "from YouTube/Spotify/Soundcloud/Twitch",
    )
    @app_commands.describe(query="search request or URL")
    async def play_audio(
        interaction: discord.Interaction, *, query: str
    ) -> None:
        player = await ensure_voice_channel(interaction)

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = interaction.channel
        elif player.home != interaction.channel:
            await interaction.response.send_message(
                f"You can only play songs in {player.home.mention},"
                + " as the player has already started there."
            )
            return

        tracks = await wavelink.Playable.search(
            query, source=TrackSource.YouTube
        )

        if not tracks:
            await interaction.response.send_message(
                f"No search results for query *{query}*"
            )

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await interaction.response.send_message(
                f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.response.send_message(
                f"Added **`{track}`** to the queue."
            )

        await start_playing(player)

    @client.tree.command(name="outro", description="epic disconnect")
    async def play_n_leave(interaction: discord.Interaction) -> None:
        player = await ensure_voice_channel(interaction)
        await interaction.response.send_message("It's time to go to sleep")

        url = config.OUTRO_VIDEO["url"]
        tracks = await wavelink.Playable.search(url)

        if not tracks:
            await interaction.response.send_message(
                f"Couldn't find the video, please verify that link is correct: '{url}'"
            )

        track = tracks[0]
        await player.play(track)

        while player.current == track and player.is_playing():
            await asyncio.sleep(0.25)

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

    async def start_playing(player: wavelink.Player) -> None:
        if player.playing or player.queue.is_empty:
            return

        next_item = player.queue.get()

        await player.play(next_item)
