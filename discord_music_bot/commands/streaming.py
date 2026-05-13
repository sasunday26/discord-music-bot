# mypy: disable-error-code=arg-type
import asyncio

import discord
import lavalink
from discord import app_commands

from .. import config
from ..client import CustomClient, LavalinkVoiceClient


def add_streaming_commands(client: CustomClient) -> None:
    @client.tree.command(
        name="play",
        description="play video/track/playlist/stream "
        "from YouTube/Spotify/Soundcloud/Twitch",
    )
    @app_commands.describe(query="search request or URL")
    async def play_audio(
        interaction: discord.Interaction, *, query: str
    ) -> None:
        if not interaction.response.is_done():
            await interaction.response.defer()

        player = await ensure_voice_channel(interaction)

        if not query.startswith("http"):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results.tracks:
            await interaction.followup.send(
                f"No search results for query *{query}*"
            )
            return

        if results.load_type == lavalink.LoadType.PLAYLIST:
            for track in results.tracks:
                player.add(requester=interaction.user.id, track=track)
            await interaction.followup.send(
                f"Added the playlist **`{results.playlist_info.name}`** ({len(results.tracks)} songs) to the queue."
            )
        else:
            track = results.tracks[0]
            player.add(requester=interaction.user.id, track=track)
            await interaction.followup.send(
                f"Added **`{track.title}`** to the queue."
            )

        if not player.is_playing:
            await player.play()

    @client.tree.command(name="outro", description="epic disconnect")
    async def play_n_leave(interaction: discord.Interaction) -> None:
        if not interaction.response.is_done():
            await interaction.response.defer()

        player = await ensure_voice_channel(interaction)
        await interaction.followup.send("It's time to go to sleep")

        url = config.OUTRO_VIDEO["url"]
        results = await player.node.get_tracks(url)

        if not results or not results.tracks:
            await interaction.followup.send(
                f"Couldn't find the video, please verify that link is correct: '{url}'"
            )
            return

        track = results.tracks[0]

        player.queue.clear()
        
        # lavalink play() instantly plays track, overriding current
        await player.play(track)

        while player.current and player.current.identifier == track.identifier and player.is_playing:
            await asyncio.sleep(0.25)

            if player.position >= config.OUTRO_VIDEO["timestamp_ms"]:
                voice = None
                if isinstance(interaction.user, discord.Member):
                    voice = interaction.user.voice

                if voice and voice.channel:
                    voice_channel = voice.channel
                    background_tasks = set()

                    for member in voice_channel.members:
                        if not member.bot:
                            task = asyncio.create_task(member.move_to(None))
                            background_tasks.add(task)
                            task.add_done_callback(background_tasks.discard)

                if interaction.guild and interaction.guild.voice_client:
                    await interaction.guild.voice_client.disconnect(force=False)
                await client.change_presence(status=discord.Status.idle)
                break

    async def ensure_voice_channel(
        interaction: discord.Interaction,
    ) -> lavalink.DefaultPlayer:
        if not interaction.user:
            raise discord.DiscordException("interaction.user is None")

        if not isinstance(interaction.user, discord.Member):
            raise discord.DiscordException(
                "interaction.user is not a discord.Member object"
            )

        author_voice = interaction.user.voice

        if not author_voice or not author_voice.channel:
            await interaction.followup.send(
                "You're not in a voice channel"
            )
            raise discord.DiscordException("interaction.user.voice is None")

        if not interaction.guild:
            raise discord.DiscordException("interaction.guild is None")

        player = interaction.client.lavalink.player_manager.create(interaction.guild.id)
        player.store("channel_id", interaction.channel.id)

        if not interaction.guild.voice_client:
            await author_voice.channel.connect(cls=LavalinkVoiceClient)
        elif author_voice.channel != interaction.guild.voice_client.channel:
            await interaction.followup.send(
                "You're in a different channel"
            )
            raise discord.DiscordException(
                "user is in a different voice channel"
            )

        return player
