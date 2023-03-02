# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

WORKDIR /app

RUN ["pip", "install", "poetry"]

COPY pyproject.toml ./

RUN ["poetry", "config", "virtualenvs.create", "false"]
RUN ["poetry", "install", "--no-root", "--only", "main"]

CMD ["poetry", "run", "python", "-m", "discord_music_bot"]

COPY discord_music_bot discord_music_bot
