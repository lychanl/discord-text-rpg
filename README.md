# discord-text-rpg
A text rpg game meant for discord bot as UI. It currently has only command line UI (for testing purposes), but starting with a future version it will be run either as a discord bot or a command line text adventure game.

It is a hobby project. If you are interested in developement, feel free to add an issue or pull request.

## Command line game

It requires python version 3 and PyYAML package.

To run the game:

 - Enter `code` directory
 - Run `python3 main.py --world ../worlds/default cli`
 - Try it! Create player with `start` command, and try commands `me` or `here` to see what's going on and what else can you do!

## Progress:

I'm working to create something that could be called the _alpha_ version.

Goals (developement):
 - [x] Fully configurable worlds
 - [x] Localized texts
 - [ ] Discord bot UI (single global game, for now)
 - [ ] In-game help

Goals (gameplay):
 - [x] Creating a player
 - [x] Locations, travelling
 - [x] Action points system, with regenerating action points
 - [ ] Location-based actions
 - [ ] Items, resources, trading (with 'NPCs' only, for now)
 - [ ] Monsters, random encounters, fighting
