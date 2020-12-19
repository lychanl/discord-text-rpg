from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.route import Route


class Location:
    def __init__(self):
        self._routes = []

    def add_route(self, route: 'Route'):
        self._routes.append(route)

    @property
    def routes(self) -> Sequence['Route']:
        return self._routes
