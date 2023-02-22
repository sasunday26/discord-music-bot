from environs import Env

env = Env()
env.read_env(override=True)


with env.prefixed("DISCORD_"):
    DISCORD = {
        "COMMAND_PREFIX": env.str("COMMAND_PREFIX"),
        "TOKEN": env.str("BOT_TOKEN"),
    }

YDL_OPTIONS = env.json("YOUTUBE_DL_OPTIONS")

LOGGING_CONFIG = env.json("LOGGING_CONFIG")
