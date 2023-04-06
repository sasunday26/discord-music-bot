from ..client import CustomClient
from .audio import add_audio_commands
from .queue import add_queue_commands
from .streaming import add_streaming_commands


def add_commands(client: CustomClient) -> None:
    add_audio_commands(client)
    add_queue_commands(client)
    add_streaming_commands(client)
