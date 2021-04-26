# discord-text-rpg
A text rpg game meant for discord bot as UI. It currently has only command line UI (for testing purposes), but starting with a future version it will be run either as a discord bot or a command line text adventure game.

It is a hobby project. If you are interested in developement, feel free to add an issue or pull request.

## Command line game

It requires python version 3.7 or above and packages from `requirements-cli.txt` (PyYAML).

To run the game:

 - Run `python3 code/main.py --world worlds/default cli`
 - Try it! Create player with `start` command, and try commands `me` or `here` to see what's going on and what else can you do! (`help` might be useful too)

## Discord game

It requires python version 3.7 or above and packages from `requirements.txt` (PyYAML, discord).

To run the game:

 - Prepare a discord bot that you want to use.
 - Prepare configuration file - specify at least the bot token, but you may want to limit the game to a single channel or specify the prefix. See `discord.sample.yaml` for an example.
 - Run `python3 code/main.py --world worlds/default --client-config your-discord-config.yaml discord`

WARNING: The game will reset if the program is reset. This will change in future version.

## Progress:

For a list of features for future versions see [https://github.com/lychanl/discord-text-rpg/issues]

## Changelog

#### 0.0.1
 - configurable worlds
 - localized texts
 - discord bot UI (single global game, for now)
 - in-game help
 - creating a player
 - locations, travelling
 - action points system, with regenerating action points
 - location-based actions
 - player-based actions
 - items, resources, trading (with 'NPCs' only, for now)
 - skills
 - monsters, fighting
