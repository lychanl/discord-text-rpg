from dtrpg.data.persistency.persistency import Persistency
from dtrpg.core import Game, GameObject, QuitGameException
from dtrpg.utils import similarity_with_wildcards

import re
import signal

from typing import Any, Hashable, Iterable, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.events import Action, EventResult


class ArgumentError(Exception):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class TextIO:
    def __init__(self, game: Game, save_path: str = None, **kwargs):
        self._game = game
        self._persistency = Persistency(game)
        self._basic_commands = {
            game.config.strings['START']: self._start,
        }

        self._save_path = save_path

        if save_path:
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

    def _get_object(self, name: str, t: type) -> object:
        if not name:
            return None
        if issubclass(t, GameObject):
            for obj in self._game.game_objects(t):
                if 'NAME' in obj.strings and name == obj.strings['NAME']:
                    return obj
                if 'REGEX_NAME' in obj.strings and re.fullmatch(obj.strings['REGEX_NAME'], name):
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

    def action(self, player_id: Hashable, command: str) -> Sequence['EventResult']:
        player = self._game.player(player_id)

        argument_error = None
        best_match = None

        for action in player.available_actions:
            match = re.fullmatch(action.strings['REGEX'], command, flags=re.IGNORECASE)
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
            self._possibly_save()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
