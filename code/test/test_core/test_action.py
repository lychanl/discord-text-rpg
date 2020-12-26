import unittest

import dtrpg.core.action as action
import dtrpg.core.player as player


class TestPlayer(unittest.TestCase):
    def test_resource_change_action(self) -> None:
        a = action.ResourceChangesAction()
        rc1 = player.ResourceChange()
        rc1.id = 'r1'
        rc1.value = -1
        rc2 = player.ResourceChange()
        rc2.id = 'r2'
        rc2.value = 4
        a.resource_changes = [rc1, rc2]

        p = player.Player()
        r1 = player.Resource()
        r1.value = 2
        r2 = player.Resource()
        r2.value = 3
        p.resources = {'r1': r1, 'r2': r2}

        e = a.take(p)

        self.assertEqual(p.resources['r1'].value, 1)
        self.assertEqual(p.resources['r2'].value, 7)
        self.assertEqual(e.resource_changes[r1], -1)
        self.assertEqual(e.resource_changes[r2], 4)

    def test_action_cost(self) -> None:
        a = action.ResourceChangesAction()
        rc1 = player.ResourceCost()
        rc1.id = 'r1'
        rc1.cost = 1
        rc2 = player.ResourceCost()
        rc2.id = 'r2'
        rc2.cost = 4
        a.costs = [rc1, rc2]

        p = player.Player()
        r1 = player.Resource()
        r1.value = 2
        r2 = player.Resource()
        r2.value = 4
        p.resources = {'r1': r1, 'r2': r2}

        self.assertTrue(a.check_requirements(p))

        a.take(p)

        self.assertEqual(p.resources['r1'].value, 1)
        self.assertEqual(p.resources['r2'].value, 0)

    def test_action_cost_insufficient(self) -> None:
        a = action.ResourceChangesAction()
        rc1 = player.ResourceCost()
        rc1.id = 'r1'
        rc1.cost = 1
        rc2 = player.ResourceCost()
        rc2.id = 'r2'
        rc2.cost = 4
        a.costs = [rc1, rc2]

        p = player.Player()
        r1 = player.Resource()
        r1.value = 2
        r2 = player.Resource()
        r2.value = 3
        p.resources = {'r1': r1, 'r2': r2}

        self.assertFalse(a.check_requirements(p))
        self.assertRaises(player.InsufficientResourceError, lambda: a.take(p))
        self.assertEqual(p.resources['r1'].value, 2)
        self.assertEqual(p.resources['r2'].value, 3)
