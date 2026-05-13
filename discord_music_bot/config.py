from environs import Env

env = Env()
env.read_env(override=True)


BOT_TOKEN: str = env.str("DISCORD_BOT_TOKEN")

with env.prefixed("LAVALINK_NODE_"):
    LAVALINK_CONFIG: dict = {
        "host": env.str("HOST"),
        "port": env.int("PORT"),
        "password": env.str("PASSWORD"),
    }

with env.prefixed("OUTRO_VIDEO_"):
    OUTRO_VIDEO: dict = {
        "url": env.str("URL"),
        "timestamp_ms": env.int("TIMESTAMP_MS"),
    }

LEAVE_AFTER: int = env.int("LEAVE_EMPTY_CHANNEL_AFTER_SEC")

LOGGING_CONFIG: dict = env.json("LOGGING_CONFIG")
