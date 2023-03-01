from datetime import timedelta


def format_timedelta(delta: timedelta) -> str:
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (f"{hours}" if hours > 0 else "") + f"{minutes}:{seconds:02d}"
