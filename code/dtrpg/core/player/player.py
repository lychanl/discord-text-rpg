from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.route import Location
    from dtrpg.core.map.route import Route


class Player:
    def __init__(self):
        self._location = None

    @property
    def location(self) -> 'Location':
        return self._location

    @location.setter
    def location(self, location: 'Location'):
        self._location = location

    def move(self, route: 'Route') -> 'Location':
        self._location = route.other(self._location)


class PlayerFactory:
    def __init__(self):
        self._default_location = None

    @property
    def default_location(self) -> 'Location':
        return self._default_location

    @default_location.setter
    def default_location(self, location: 'Location'):
        self._default_location = location

    def create(self) -> 'Player':
        player = Player()

        player.location = self.default_location

        return player
