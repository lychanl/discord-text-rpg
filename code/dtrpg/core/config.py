from dtrpg.core.game_object import GameObject
from dtrpg.core.player import PlayerFactory


class Config(GameObject):
    def __init__(self):
        super().__init__()
        self._player_factory = None

    @property
    def player_factory(self) -> PlayerFactory:
        return self._player_factory

    @player_factory.setter
    def player_factory(self, player_factory: PlayerFactory) -> None:
        self._player_factory = player_factory
