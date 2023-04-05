from discord import app_commands

from discord_music_bot.commands.audio import add_audio_commands

# from discord_music_bot.commands.queue import add_queue_commands
# from discord_music_bot.commands.streaming import add_streaming_commands


def add_commands(tree: app_commands.CommandTree) -> None:
    add_audio_commands(tree)
    # add_queue_commands()
    # add_streaming_commands()
