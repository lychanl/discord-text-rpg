import unittest

import dtrpg.core.map as map_


class TestMap(unittest.TestCase):
    def test_route_location_setting(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()
        loc3 = map_.Location()

        route = map_.Route()

        route.locations = loc1, loc2

        self.assertIn(loc1, route.locations)
        self.assertIn(loc2, route.locations)
        self.assertNotIn(loc3, route.locations)
        self.assertIs(route.other(loc1), loc2)
        self.assertIs(route.other(loc2), loc1)
        self.assertRaises(ValueError, lambda: route.other(loc3))

        self.assertIn(route, loc1.routes)
        self.assertIn(route, loc2.routes)
