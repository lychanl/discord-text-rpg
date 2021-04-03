from dtrpg.core import Game, GameObject

import re

from typing import Any, Hashable, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action, Event


class ArgumentError(Exception):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class TextIO:
    def __init__(self, game: Game):
        self._game = game
        self._basic_commands = {
            'start': self._start,
        }

    def command(self, player_id: Hashable, command: str) -> str:
        try:
            command = command.strip().lower()
            if command in self._basic_commands:
                return self._basic_commands[command](player_id)
            event = self.action(player_id, command)
            if event:
                return event.strings['EVENT_NOW']
        except Exception as e:
            string = f'EXCEPTION_{type(e).__name__}'
            if string in self._game.config.strings:
                return self._game.config.strings[string, {'e': e}]
            else:
                raise

        return self._invalid_command()

    def _get_object(self, name: str, t: type) -> object:
        if not name:
            return None
        if issubclass(t, GameObject):
            for obj in self._game.game_objects(t):
                if 'NAME' in obj.strings and name == obj.strings['NAME']:
                    return obj
                if 'REGEX_NAME' in obj.strings and re.match(obj.strings['REGEX_NAME'], name):
                    return obj
            raise ArgumentError(name)
        else:
            try:
                return t(name)
            except ValueError:
                raise ArgumentError(name)

    def _parse_args(self, action: 'Action', match: re.Match) -> Iterable[object]:
        return {
            arg: self._get_object(value, action.args[arg]) for arg, value in match.groupdict().items() if value
        }

    def action(self, player_id: Hashable, command: str) -> 'Event':
        player = self._game.player(player_id)

        argument_error = None

        for action in player.available_actions:
            match = re.fullmatch(action.strings['REGEX'], command, flags=re.IGNORECASE)
            if match:
                try:
                    args = self._parse_args(action, match)
                    return action.take(player, **args)
                except ArgumentError as e:
                    argument_error = e

        if argument_error:
            raise argument_error

        return None

    def _start(self, player_id: Hashable) -> str:
        player = self._game.create_player(player_id)
        return player.strings['WELCOME']

    def _invalid_command(self) -> str:
        return self._game.config.strings['INVALID_COMMAND']

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
