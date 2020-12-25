from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.route import Location
    from dtrpg.core.action import Action


class Player(GameObject):
    def __init__(self):
        super().__init__()
        self._location = None

    @property
    def location(self) -> 'Location':
        return self._location

    @location.setter
    def location(self, location: 'Location') -> None:
        self._location = location

    @property
    def available_actions(self) -> Iterable['Action']:
        return self._location.travel_actions


class PlayerFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Player)
        self._default_location = None

    @property
    def default_location(self) -> 'Location':
        return self._default_location

    @default_location.setter
    def default_location(self, location: 'Location') -> None:
        self._default_location = location

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location

        return player
