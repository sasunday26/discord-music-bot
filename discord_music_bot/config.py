from environs import Env

env = Env()
env.read_env(override=True)


with env.prefixed("DISCORD_"):
    BOT_TOKEN: str = env.str("BOT_TOKEN")
    GUILD_ID: int = env.int("GUILD_ID")

with env.prefixed("WAVELINK_NODE_"):
    WAVELINK_CONFIG: dict = {
        "uri": env.str("URI"),
        "password": env.str("PASSWORD"),
    }

with env.prefixed("SPOTIFY_"):
    SPOTIFY_CONFIG: dict = {
        "client_id": env.str("CLIENT_ID"),
        "client_secret": env.str("CLIENT_SECRET"),
    }

LOGGING_CONFIG: dict = env.json("LOGGING_CONFIG")
