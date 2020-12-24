from dtrpg.core.config import Config
from dtrpg.core.player import Player

from typing import Any


class DuplicatePlayerError(Exception):
    pass


class InvalidPlayerError(Exception):
    pass


class Game:
    def __init__(self, config: Config):
        self._config = config
        self._players = {}

    def config(self) -> Config:
        return self._config

    def create_player(self, id_: Any) -> Player:
        if id_ in self._players:
            raise DuplicatePlayerError

        self._players[id_] = self._config.player_factory.create()
        return self._players[id_]

    def player(self, id_: Any) -> Player:
        try:
            return self._players[id_]
        except KeyError:
            raise InvalidPlayerError
