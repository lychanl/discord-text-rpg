import unittest
import unittest.mock as mock

import dtrpg.core.events as events
import dtrpg.core.item as item
import dtrpg.core.player as player


class TestEvents(unittest.TestCase):
    def test_resource_change_event(self) -> None:
        a = events.ResourceChangesEvent()

        res1 = player.Resource()
        res2 = player.Resource()

        rc1 = player.ResourceChange()
        rc1.resource = res1
        rc1.value = -1
        rc2 = player.ResourceChange()
        rc2.resource = res2
        rc2.value = 4
        a.resource_changes = [rc1, rc2]

        p = player.Player()
        r1 = player.PlayerResource()
        r1.resource = res1
        r1.value = 2
        r2 = player.PlayerResource()
        r2.resource = res2
        r2.value = 3
        p.resources = {res1: r1, res2: r2}

        e = a.fire(p)

        self.assertEqual(p.resources[res1].value, 1)
        self.assertEqual(p.resources[res2].value, 7)
        self.assertEqual(e.resource_changes[res1], -1)
        self.assertEqual(e.resource_changes[res2], 4)

    def test_item_receive_event(self) -> None:
        a = events.ItemReceiveEvent()
        i = item.Item()
        i.max_stack = 1

        a.item_factory = item.ItemStackFactory()
        a.item_factory.item = i
        a.item_factory.stack = 2
        p = player.Player()
        p.items = item.Container()
        p.items.max_items = 3

        e1 = a.fire(p)
        self.assertIs(e1.item, i)
        self.assertEqual(e1.number, 2)
        self.assertIsNone(e1.overflow)
        self.assertEqual(p.items.count(i), 2)

        e2 = a.fire(p)
        self.assertIs(e2.item, i)
        self.assertEqual(e2.number, 2)
        self.assertIs(e2.overflow.stack.item, i)
        self.assertEqual(e2.overflow.stack.stack, 1)
        self.assertEqual(p.items.count(i), 3)

    def test_action_cost(self) -> None:
        a = events.Action()

        res1 = player.Resource()
        res2 = player.Resource()

        rc1 = player.ResourceCost()
        rc1.resource = res1
        rc1.cost = 1
        rc2 = player.ResourceCost()
        rc2.resource = res2
        rc2.cost = 4
        a.costs = [rc1, rc2]
        a.event = events.InfoEvent()

        p = player.Player()
        r1 = player.PlayerResource()
        r1.value = 2
        r2 = player.PlayerResource()
        r2.value = 4
        p.resources = {res1: r1, res2: r2}

        self.assertTrue(a.check_requirements(p))

        a.take(p)

        self.assertEqual(p.resources[res1].value, 1)
        self.assertEqual(p.resources[res2].value, 0)

    def test_action_cost_insufficient(self) -> None:
        a = events.Action()

        res1 = player.Resource()
        res2 = player.Resource()

        rc1 = player.ResourceCost()
        rc1.resource = res1
        rc1.cost = 1
        rc2 = player.ResourceCost()
        rc2.resource = res2
        rc2.cost = 4
        a.costs = [rc1, rc2]
        a.event = events.InfoEvent()

        p = player.Player()
        r1 = player.PlayerResource()
        r1.value = 2
        r2 = player.PlayerResource()
        r2.value = 3
        p.resources = {res1: r1, res2: r2}

        self.assertFalse(a.check_requirements(p))
        self.assertRaises(player.InsufficientResourceError, lambda: a.take(p))
        self.assertEqual(p.resources[res1].value, 2)
        self.assertEqual(p.resources[res2].value, 3)

    def test_skill_event(self) -> None:
        s = player.Skill()
        p = player.Player()
        ps = player.PlayerSkill()
        ps.skill = s
        ps.value = 1
        p.skills = {s: ps}

        e = events.SkillTestEvent()
        e.test = mock.Mock()

        sret = object()
        fret = object()

        e.success = mock.Mock()
        e.failure = mock.Mock()

        e.test.test.return_value = True
        e.success.fire.return_value = sret
        e.failure.fire.return_value = fret

        params = {'success.param': 4}

        self.assertIs(e.fire(p, **params), sret)
        e.success.fire.assert_called_once_with(p, param=4)
        e.failure.assert_not_called()

        e.test.test.return_value = False
        e.success.reset_mock()
        e.failure.reset_mock()

        self.assertIs(e.fire(p, **params), fret)
        e.success.assert_not_called()
        e.failure.fire.assert_called_once_with(p)
