import unittest
from unittest import mock

import dtrpg.core.item as item
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
        cf = item.ContainerFactory()

        factory.default_location = loc
        factory.container_factory = cf

        p = factory.create()

        self.assertIs(p.location, loc)
        self.assertIsInstance(p.items, item.Container)

    def test_player_factory_resources(self) -> None:
        factory = player.PlayerFactory()
        rf = player.PlayerResourceFactory()
        res = player.Resource()
        rf.resource = res
        rf.initial = 1

        factory.resource_factories = [rf]
        factory.container_factory = item.ContainerFactory()

        p = factory.create()

        self.assertIn(res, p.resources)
        self.assertEqual(p.resources[res].value, 1)
        self.assertIs(p.resources[res].resource, res)


class TestResourceFactory(unittest.TestCase):
    def test_resource_factory(self) -> None:
        factory = player.PlayerResourceFactory()
        res = player.Resource()
        factory.initial = 1
        factory.max = 10
        factory.base_gen_rate = 0.5
        factory.resource = res
        clock = mock.Mock()
        clock.configure_mock(**{'now.return_value': None, 'now_with_diff.return_value': (None, 5)})
        factory.clock = clock

        r = factory.create()

        self.assertEqual(r.value, 1)
        self.assertEqual(r.max, 10)
        self.assertEqual(r.base_gen_rate, 0.5)
        self.assertIs(r.resource, res)
        self.assertIs(r.clock, clock)


class TestResource(unittest.TestCase):
    def test_resource_max(self) -> None:
        r = player.PlayerResource()
        r.max = 10
        r.value = 20
        self.assertEqual(r.value, 10)
        r.max = 5
        self.assertEqual(r.value, 5)

    def test_resource_gen(self) -> None:
        time = object()
        nexttime = object()
        clock = mock.Mock()
        clock.configure_mock(**{'now.return_value': time, 'now_with_diff.return_value': (nexttime, 5)})

        r = player.PlayerResource()
        r.value = 10
        r.base_gen_rate = 0.5
        r.clock = clock

        self.assertEqual(r.value, 12)
        clock.now_with_diff.assert_called_with(time)
        self.assertEqual(r.value, 15)
        clock.now_with_diff.assert_called_with(nexttime)

    def test_resource_gen_with_max(self) -> None:
        time = object()
        nexttime = object()
        clock = mock.Mock()
        clock.configure_mock(**{'now.return_value': time, 'now_with_diff.return_value': (nexttime, 5)})

        r = player.PlayerResource()
        r.value = 10
        r.max = 12
        r.base_gen_rate = 0.5
        r.clock = clock

        self.assertEqual(r.value, 12)
        self.assertEqual(r.value, 12)
        self.assertEqual(r.value, 12)
        r.value = 5
        self.assertEqual(r.value, 7)
