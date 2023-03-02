# Discord Music Bot

![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/andrewyazura/discord-music-bot?include_prereleases)
![GitHub license](https://img.shields.io/github/license/andrewyazura/discord-music-bot)

Discord bot for playing music in your discord server.

## Development environment setup

### Requirements

* Docker Engine
* Docker Compose
* Python 3.11
  * I recommend using `pyenv` to control available python version
* Poetry

### Installation

Install all dependencies specified in `pyproject.toml`:

```bash
$ poetry env use 3.11

Creating virtualenv discord-music-bot
Using virtualenv: /path/to/virtual/environment

$ poetry install

...
Installing the current project: discord-music-bot
```

Inside the repository directory, install `pre-commit`'s hook:

```bash
$ poetry run pre-commit install

pre-commit installed at .git/hooks/pre-commit
```

Now, try running all checks to verify installation success.
First run might take a couple of minutes to install all the hooks.

```bash
$ poetry run pre-commit run -a

fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
black....................................................................Passed
mypy.....................................................................Passed
pylint...................................................................Passed
pyupgrade................................................................Passed
poetry-check.............................................................Passed
```

## Running the project

Before running the project, you have to create configuration files.
There are examples in the repo: `.env.example` and `lavalink.example.yaml`, so you can copy those and fill in the data.

### For development

To run the project locally, there is a separate Docker compose configuration in `docker-compose.dev.yaml`.
You can run the project using base and `dev` compose configs:

```bash
$ docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up

[+] Running X/X
...
```

### In production

In production you'll have to build the image and then run it using Docker Compose:

```bash
$ docker build --tag discord-music-bot .

[+] Building Xs (X/X) FINISHED
...

$ docker compose up -d

[+] Running X/X
...
```
