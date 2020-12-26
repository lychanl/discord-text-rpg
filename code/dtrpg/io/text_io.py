from dtrpg.core import Game, InvalidPlayerError, DuplicatePlayerError

import re

from typing import Any, Hashable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Event


class TextIO:
    def __init__(self, game: Game):
        self._game = game
        self._basic_commands = {
            'start': self._start,
            'here': self._here,
            'me': self._me
        }

    def command(self, player_id: Hashable, command: str) -> str:
        try:
            command = command.strip().lower()
            if command in self._basic_commands:
                return self._basic_commands[command](player_id)
            event = self.action(player_id, command)
            if event:
                return event.strings['EVENT_NOW']
        except InvalidPlayerError:
            return self._game.config.strings['INVALID_PLAYER']

        return self._invalid_command()

    def action(self, player_id: Hashable, command: str) -> 'Event':
        player = self._game.player(player_id)
        for action in player.available_actions:
            match = re.fullmatch(action.strings['REGEX'], command, flags=re.IGNORECASE)
            if match:
                return action.take(player, match.groups())

        return None

    def _here(self, player_id: Hashable) -> str:
        return self._game.player(player_id).location.strings['HERE']

    def _me(self, player_id: Hashable) -> str:
        return self._game.player(player_id).strings['ME']

    def _start(self, player_id: Hashable) -> str:
        try:
            player = self._game.create_player(player_id)
            return player.strings['WELCOME']
        except DuplicatePlayerError:
            return self._game.config.strings['DUPLICATE_PLAYER']

    def _invalid_command(self) -> str:
        return self._game.config.strings['INVALID_COMMAND']

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
