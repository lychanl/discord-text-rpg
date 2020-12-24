from dtrpg.core.game_object import GameObject

from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.route import Route


class Location(GameObject):
    def __init__(self):
        super().__init__()
        self._routes = []

    def add_route(self, route: 'Route') -> None:
        self._routes.append(route)

    @property
    def routes(self) -> Sequence['Route']:
        return self._routes
