import os
from dtrpg.data.persistency.persistency import Persistency
from dtrpg.data.parsing.parser import ArgumentError
from dtrpg.core import Game, QuitGameException
from dtrpg.utils import similarity_with_wildcards

import re
import signal

from typing import Any, Hashable, Iterable, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.events import Action, EventResult


class TextIO:
    def __init__(self, game: Game, save_path: str = None, **kwargs):
        self._game = game
        self._persistency = Persistency(game)
        self._basic_commands = {
            game.config.strings['START']: self._start,
        }

        self._save_path = save_path

        if save_path and os.path.exists(save_path):
            print("Restoring game from save...")
            self._persistency.load(save_path)

        signal.signal(signal.SIGINT, self._interrupt_handler)

    def _possibly_save(self):
        if self._save_path:
            self._persistency.save(self._save_path)
            print(f"Game saved to {self._save_path}")

    def _interrupt_handler(self, signum, frame) -> None:
        raise KeyboardInterrupt

    def command(self, player_id: Hashable, command: str) -> Sequence[str]:
        try:
            command = command.strip().lower()
            if command in self._basic_commands:
                return self._basic_commands[command](player_id)
            events = self.action(player_id, command)

            if events:
                return [event.strings['EVENT_NOW'] for event in events]
            else:
                return [self._game.config.strings['EMPTY']]
        except Exception as e:
            string = f'EXCEPTION_{type(e).__name__}'

            if isinstance(e, QuitGameException):
                self._exit(player_id)

            if string in self._game.config.strings:
                return [self._game.config.strings[string, {'e': e}]]
            else:
                raise

    def _parse_args(self, action: 'Action', match: re.Match) -> Iterable[object]:
        return {
            arg: action.args[arg].parser(value) for arg, value in match.groupdict().items() if value
        }

    def check_action_command_match(self, action, command):
        return re.fullmatch(action.strings['REGEX'], command, flags=re.IGNORECASE + re.MULTILINE + re.DOTALL)

    def action(self, player_id: Hashable, command: str) -> Sequence['EventResult']:
        player = self._game.player(player_id)

        argument_error = None
        best_match = None

        for action in player.available_actions:
            match = self.check_action_command_match(action, command)
            if match:
                try:
                    args = self._parse_args(action, match)
                    return action.take(player, **args)
                except ArgumentError as e:
                    argument_error = e
            else:
                sim = similarity_with_wildcards(command, action.strings['HINT'])
                if not best_match or best_match[0] < sim:
                    best_match = sim, action

        if argument_error:
            raise argument_error

        if player.invalid_action_event:
            player.events.register(
                player.invalid_action_event,
                best_action=best_match[1], best_similarity=best_match[0]
            )
            return player.events.fire_all()
        return []

    def _start(self, player_id: Hashable) -> Sequence[str]:
        player = self._game.create_player(player_id)
        return [player.strings['WELCOME']]

    def _exit(self, player_id: Hashable) -> Sequence[str]:
        self._game.remove_player(player_id)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        try:
            self._run(*args, **kwargs)
        except KeyboardInterrupt:
            pass
        self._possibly_save()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
