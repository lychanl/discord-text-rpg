import unittest

import dtrpg.core.map as map_
import dtrpg.core.player as player


class TestPlayer(unittest.TestCase):
    def test_player_move(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()

        route = map_.Route()
        route.locations = loc1, loc2

        p = player.Player()
        p.location = loc1

        p.move(route)

        self.assertIs(p.location, loc2)


class TestPlayerFactory(unittest.TestCase):
    def test_player_factory(self) -> None:
        factory = player.PlayerFactory()
        loc = map_.Location()

        factory.default_location = loc

        p = factory.create()

        self.assertIs(p.location, loc)
