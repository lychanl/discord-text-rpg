from dtrpg.core import Game, InvalidPlayerError, DuplicatePlayerError

from typing import Any, Iterable


class TextIO:
    def __init__(self, game: Game):
        self._game = game
        self._commands = {
            'start': self._start,
            'here': self._here
        }

    def command(self, player_id: Any, command: str, *args: Iterable[str]) -> str:
        return self._commands.get(command, self._invalid_command)(player_id, *args)

    def _here(self, player_id: Any, *args: Iterable[str]) -> str:
        if args:
            self._invalid_args()
        try:
            return self._game.player(player_id).location.strings['YOU_ARE_HERE']
        except InvalidPlayerError:
            return self._game.config().strings['INVALID_PLAYER']

    def _start(self, player_id: Any, *args: Iterable[str]) -> str:
        if args:
            self._invalid_args()
        try:
            player = self._game.create_player(player_id)
            return player.strings['WELCOME']
        except DuplicatePlayerError:
            return self._game.config().strings['DUPLICATE_PLAYER']

    def _invalid_args(self) -> str:
        return self._game.config().strings['INVALID_ARGS']

    def _invalid_command(self, player_id: Any, *args: Iterable[str]) -> str:
        return self._game.config().strings['INVALID_COMMAND']

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
