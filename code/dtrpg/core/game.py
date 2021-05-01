from dtrpg.core.config import Config
from dtrpg.core.creature import Player
from dtrpg.core.events import Event, EventResult

from typing import Hashable, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.game_object import GameObject


class QuitGameException(Exception):
    pass


class DuplicatePlayerError(Exception):
    pass


class InvalidPlayerError(Exception):
    pass


class QuitGameEvent(Event):
    def __init__(self):
        super().__init__(EventResult)

    def _fire(self, player: 'Player') -> None:
        raise QuitGameException


class Game:
    def __init__(self, config: Config, world_objects: Iterable['GameObject']):
        self._config = config
        self._players = {}
        self._global_objects = world_objects

    @property
    def config(self) -> Config:
        return self._config

    def create_player(self, id_: Hashable) -> Player:
        if id_ in self._players:
            raise DuplicatePlayerError

        self._players[id_] = self._config.player_factory.create()
        return self._players[id_]

    def remove_player(self, id_: Hashable) -> None:
        del self._players[id_]

    def player(self, id_: Hashable) -> Player:
        try:
            return self._players[id_]
        except KeyError:
            raise InvalidPlayerError

    def game_objects(self, clss: type) -> Iterable['GameObject']:
        return [o for o in self._global_objects if isinstance(o, clss)]
