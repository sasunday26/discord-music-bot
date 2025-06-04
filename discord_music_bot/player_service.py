import re
from datetime import timedelta

import discord
import wavelink
from wavelink import QueueMode, AutoPlayMode
from wavelink.types.filters import Equalizer

from .helpers import format_timedelta
from .client import CustomClient


async def toggle_pause(player: wavelink.Player) -> str:
    if not player.playing:
        return "Not playing"

    await player.pause(not player.paused)
    return "Paused" if player.paused else "Resumed"


async def disconnect_player(player: wavelink.Player, client: CustomClient) -> str:
    await player.disconnect()
    await client.change_presence(status=discord.Status.idle)
    return "Ok"


async def set_player_volume(player: wavelink.Player, volume: int) -> str:
    await player.set_volume(volume)
    return f"Volume set to {volume}%"


def parse_timestamp(position: str) -> timedelta | None:
    matches = re.match(r"^(?:(?:(\d+):)?(\d+):)?(\d+)$", position)
    if not matches:
        return None

    hours, minutes, seconds = (int(m) if m else 0 for m in matches.groups())
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


async def seek_player(player: wavelink.Player, position: timedelta) -> str:
    if not player.current:
        return "Not playing anything right now"

    duration = timedelta(seconds=player.current.length)
    if duration < position:
        return (
            f"Track's total length is {format_timedelta(duration)}, "
            "that is too far"
        )

    await player.seek(position.seconds * 1000)
    return f"Seeking to {format_timedelta(position)}"


def parse_equalizer(settings: str) -> list[Equalizer]:
    bands: list[Equalizer] = []
    for param in settings.strip().split(" "):
        if not param:
            continue

        band, gain = param.split(":")
        bands.append(Equalizer(band=int(band), gain=float(gain)))
    return bands


async def apply_equalizer_settings(
    player: wavelink.Player, bands: list[Equalizer]
) -> str:
    filters: wavelink.Filters = player.filters
    filters.equalizer.set(bands=bands)

    try:
        await player.set_filters(filters, seek=True)
    except ValueError:
        return "Invalid value"

    return "Equalizer added"


async def set_playback_speed(
    player: wavelink.Player, speed: float, pitch: float = 1.0
) -> str:
    filters: wavelink.Filters = player.filters
    filters.timescale.set(speed=speed, pitch=pitch)

    await player.set_filters(filters, seek=True)
    return "New speed applied"


async def reset_player_filters(player: wavelink.Player) -> str:
    filters: wavelink.Filters = player.filters
    filters.reset()

    await player.set_filters(filters, seek=True)
    return "Filters reset"


def now_playing_embed(player: wavelink.Player) -> discord.Embed:
    track = player.current
    embed = discord.Embed(title=track.title, colour=discord.Colour.random())

    if track.author:
        embed.add_field(name="Author", value=track.author)

    position = timedelta(seconds=player.position // 1000)
    embed.add_field(name="Position", value=format_timedelta(position))

    duration = timedelta(seconds=track.length // 1000)
    embed.add_field(name="Duration", value=format_timedelta(duration))

    if track.uri:
        embed.add_field(name="Link", value=track.uri)

    if track.artwork:
        embed.set_image(url=track.artwork)

    if track.album.name:
        embed.add_field(name="Album", value=track.album.name)

    return embed


def queue_embed(tracks: list[wavelink.Playable], title: str) -> discord.Embed:
    embed = discord.Embed(title=title, colour=discord.Colour.random())

    for i, track in enumerate(tracks, start=1):
        embed.add_field(
            name=f"`{track.title} - {track.author}`", value=str(i)
        )

    return embed


async def clear_queue(player: wavelink.Player) -> str:
    player.queue.clear()
    return "Queue cleared"


async def skip_current(player: wavelink.Player) -> str:
    skipped_item = await player.skip()
    if not skipped_item:
        return "Nothing to skip"

    return (
        f"Skipping **`{skipped_item.title} - {skipped_item.author}`**"
    )


def toggle_loop(player: wavelink.Player) -> str:
    is_looped = player.queue.mode == QueueMode.normal
    player.queue.mode = QueueMode.loop if is_looped else QueueMode.normal

    return f"Current track is {'' if is_looped else 'un'}looped"


def toggle_autoplay(player: wavelink.Player) -> str:
    player.autoplay = (
        AutoPlayMode.enabled
        if player.autoplay == AutoPlayMode.disabled
        else AutoPlayMode.disabled
    )

    state = "" if player.autoplay != AutoPlayMode.disabled else "not "
    return f"Autoplay is {state}enabled"
