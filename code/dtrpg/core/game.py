from dtrpg.core.config import Config
from dtrpg.core.clock import Clock
from dtrpg.core.player import Player

from typing import Hashable


class DuplicatePlayerError(Exception):
    pass


class InvalidPlayerError(Exception):
    pass


class Game:
    def __init__(self, config: Config):
        self._config = config
        self._clock = Clock()
        self._players = {}

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def config(self) -> Config:
        return self._config

    def create_player(self, id_: Hashable) -> Player:
        if id_ in self._players:
            raise DuplicatePlayerError

        self._players[id_] = self._config.player_factory.create()
        return self._players[id_]

    def player(self, id_: Hashable) -> Player:
        try:
            return self._players[id_]
        except KeyError:
            raise InvalidPlayerError
