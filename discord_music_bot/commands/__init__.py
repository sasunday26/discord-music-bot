from discord import app_commands

from .audio import add_audio_commands
from .queue import add_queue_commands

# from .streaming import add_streaming_commands


def add_commands(tree: app_commands.CommandTree) -> None:
    add_audio_commands(tree)
    add_queue_commands(tree)
    # add_streaming_commands(tree)
