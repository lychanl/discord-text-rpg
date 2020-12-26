import unittest

import dtrpg.core.map as map_
import dtrpg.core.player as player


class TestPlayer(unittest.TestCase):
    def test_player_move(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()

        travel_action = map_.TravelAction()
        travel_action.to = loc2
        loc1.travel_actions = [travel_action]

        p = player.Player()
        p.location = loc1

        e = travel_action.take(p)

        self.assertIs(p.location, loc2)
        self.assertIs(e.from_, loc1)
        self.assertIs(e.to, loc2)
        self.assertIs(e.player, p)


class TestPlayerFactory(unittest.TestCase):
    def test_player_factory(self) -> None:
        factory = player.PlayerFactory()
        loc = map_.Location()

        factory.default_location = loc

        p = factory.create()

        self.assertIs(p.location, loc)

    def test_player_factory_resources(self) -> None:
        factory = player.PlayerFactory()
        rf = player.ResourceFactory()
        rf.id = 'id'
        rf.initial = 1

        factory.resource_factories = [rf]

        p = factory.create()

        self.assertIn('id', p.resources)
        self.assertEqual(p.resources['id'].value, 1)


class TestResourceFactory(unittest.TestCase):
    def test_resource_factory(self) -> None:
        factory = player.ResourceFactory()
        factory.initial = 1

        r = factory.create()

        self.assertEqual(r.value, 1)
