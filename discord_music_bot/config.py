from environs import Env

env = Env()
env.read_env(override=True)


with env.prefixed("DISCORD_"):
    BOT_TOKEN: str = env.str("BOT_TOKEN")
    COMMAND_PREFIX: str = env.str("COMMAND_PREFIX")
    GUILD_IDS: list = env.list("GUILD_IDS")

FFMPEG_OPTIONS: dict = env.json("FFMPEG_OPTIONS")
YDL_OPTIONS: dict = env.json("YOUTUBE_DL_OPTIONS")

LOGGING_CONFIG: dict = env.json("LOGGING_CONFIG")
