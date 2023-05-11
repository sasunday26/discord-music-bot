from environs import Env

env = Env()
env.read_env(override=True)


with env.prefixed("DISCORD_"):
    BOT_TOKEN: str = env.str("BOT_TOKEN")
    GUILD_IDS: list[int] = env.list("GUILD_IDS", subcast=int)

with env.prefixed("WAVELINK_NODE_"):
    WAVELINK_CONFIG: dict = {
        "uri": env.str("URI"),
        "password": env.str("PASSWORD"),
    }

with env.prefixed("SPOTIFY_CLIENT_"):
    SPOTIFY_CONFIG: dict = {
        "client_id": env.str("ID"),
        "client_secret": env.str("SECRET"),
    }

with env.prefixed("OUTRO_VIDEO_"):
    OUTRO_VIDEO: dict = {
        "url": env.str("URL"),
        "timestamp_ms": env.int("TIMESTAMP_MS"),
    }

LOGGING_CONFIG: dict = env.json("LOGGING_CONFIG")
