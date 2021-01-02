from dtrpg.core import Game, GameObject, InvalidPlayerError, DuplicatePlayerError
from dtrpg.core.player import InsufficientResourceError, PlayerResource
from dtrpg.core.item import ContainerCapacityException, OfferNotFoundException, InsufficientItemsException

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
        except ArgumentError as e:
            return self._invalid_agument(e.value)
        except InvalidPlayerError:
            return self._game.config.strings['INVALID_PLAYER']
        except InsufficientResourceError as e:
            return self._insufficient_resource(e.resource, e.required)
        except InsufficientItemsException:
            return self._game.config.strings['INSUFFICIENT_ITEMS']
        except OfferNotFoundException:
            return self._game.config.strings['OFFER_NOT_FOUND']
        except ContainerCapacityException:
            return self._game.config.strings['CONTAINER_CAPACITY']

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
        for action in player.available_actions:
            match = re.fullmatch(action.strings['REGEX'], command, flags=re.IGNORECASE)
            if match:
                args = self._parse_args(action, match)
                return action.take(player, **args)

        return None

    def _here(self, player_id: Hashable) -> str:
        return self._game.player(player_id).location.strings['HERE']

    def _me(self, player_id: Hashable) -> str:
        return self._game.player(player_id).strings['ME']

    def _items(self, player_id: Hashable) -> str:
        return self._game.player(player_id).strings['ITEMS']

    def _start(self, player_id: Hashable) -> str:
        try:
            player = self._game.create_player(player_id)
            return player.strings['WELCOME']
        except DuplicatePlayerError:
            return self._game.config.strings['DUPLICATE_PLAYER']

    def _invalid_agument(self, value: str) -> str:
        return self._game.config.strings['INVALID_ARGUMENT', {'value': value}]

    def _invalid_command(self) -> str:
        return self._game.config.strings['INVALID_COMMAND']

    def _insufficient_resource(self, resource: 'PlayerResource', required: int) -> str:
        return self._game.config.strings[
            'INSUFFICIENT_RESOURCE',
            {'player_resource': resource, 'resource': resource.resource, 'required': required}
        ]

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
