from typing import cast

import discord
from discord.ext import commands


class AudioSource(discord.AudioSource):
    volume: float

    def read(self) -> bytes:
        raise NotImplementedError


class VoiceClient(discord.VoiceClient):
    source: AudioSource


class Context(commands.Context):
    """
    Replaces discord.ext.commands.Context

    Context.voice_client has a type VoiceProtocol,
    which is a concrete implementation of VoiceClient,
    therefore it must have methods .play(), .pause(),
    .resume() and others, that VoiceClient does.

    Instead, in the code, VoiceProtocol is the parent
    class of VoiceClient. Because of that mypy and pyright
    show errors in places where .play(), .pause() and
    other similar methods are used.
    """

    @property
    def voice_client(self) -> VoiceClient:
        return cast(VoiceClient, super().voice_client)
