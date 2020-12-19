from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.location import Location


class Route:
    def __init__(self):
        self._locations = (None, None)

    @property
    def locations(self) -> Tuple['Location']:
        return self._locations

    @locations.setter
    def locations(self, locs: Tuple['Location']):
        loc1, loc2 = locs
        self._locations = (loc1, loc2)
        loc1.add_route(self)
        loc2.add_route(self)

    def other(self, location: 'Location'):
        if location is self._locations[0]:
            return self._locations[1]
        elif location is self._locations[1]:
            return self._locations[0]
        else:
            raise ValueError
