from dtrpg.core.events.event_result import ExceptionEventResult
import unittest
import unittest.mock as mock

import dtrpg.core.events as events
import dtrpg.core.item as item
import dtrpg.core.creature as creature


class TestEvents(unittest.TestCase):
    def test_resource_change_event(self) -> None:
        a = events.ResourceChangesEvent()

        res1 = creature.Resource()
        res2 = creature.Resource()

        rc1 = creature.ResourceChange()
        rc1.resource = res1
        rc1.value = -1
        rc2 = creature.ResourceChange()
        rc2.resource = res2
        rc2.value = 4
        a.resource_changes = [rc1, rc2]

        p = creature.Player()
        r1 = creature.CreatureResource()
        r1.resource = res1
        r1.value = 2
        r2 = creature.CreatureResource()
        r2.resource = res2
        r2.value = 3
        p.resources = {res1: r1, res2: r2}

        e = a.fire(p)

        self.assertEqual(p.resources[res1].value, 1)
        self.assertEqual(p.resources[res2].value, 7)
        self.assertEqual(e.resource_changes[res1], -1)
        self.assertEqual(e.resource_changes[res2], 4)

    def test_item_receive_event(self) -> None:
        a = item.ItemReceiveEvent()
        i = item.Item()
        i.max_stack = 1

        a.item_factory = item.ItemStackFactory()
        a.item_factory.item = i
        a.item_factory.stack = 2
        p = creature.Player()
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

    def test_use_item(self) -> None:
        e = item.UseItemEvent()
        i = item.Item()
        p = creature.Player()
        p.items = item.Container()
        p.items.add(item.ItemStack(i))

        i.use = object()
        param = object()

        e.item = i

        e.fire(p, **{'use.param': param})

        self.assertSequenceEqual(p.events.events, [(i.use, {'param': param})])
        self.assertEqual(p.items.count(i), 1)

    def test_use_item_remove(self) -> None:
        e = item.UseItemEvent()
        i = item.Item()
        p = creature.Player()
        p.items = item.Container()
        p.items.add(item.ItemStack(i))

        i.use = object()
        i.remove_on_use = True
        param = object()

        e.item = i

        e.fire(p, **{'use.param': param})

        self.assertSequenceEqual(p.events.events, [(i.use, {'param': param})])
        self.assertEqual(p.items.count(i), 0)

    def test_use_item_insufficient(self) -> None:
        e = item.UseItemEvent()
        i = item.Item()
        p = creature.Player()
        p.items = item.Container()

        i.use = object()
        param = object()

        e.item = i

        result = e.fire(p, **{'use.param': param})
        self.assertIsInstance(result, ExceptionEventResult)

    def test_use_item_unusable(self) -> None:
        e = item.UseItemEvent()
        i = item.Item()
        p = creature.Player()
        p.items = item.Container()
        p.items.add(item.ItemStack(i))

        param = object()

        e.item = i

        result = e.fire(p, **{'use.param': param})
        self.assertIsInstance(result, ExceptionEventResult)

    def test_action_cost(self) -> None:
        a = events.Action()

        res1 = creature.Resource()
        res2 = creature.Resource()

        rc1 = creature.ResourceCost()
        rc1.resource = res1
        rc1.cost = 1
        rc2 = creature.ResourceCost()
        rc2.resource = res2
        rc2.cost = 4
        a.costs = [rc1, rc2]
        a.event = events.InfoEvent()

        p = creature.Player()
        r1 = creature.CreatureResource()
        r1.value = 2
        r2 = creature.CreatureResource()
        r2.value = 4
        p.resources = {res1: r1, res2: r2}

        self.assertTrue(a.check_requirements(p))

        a.take(p)

        self.assertEqual(p.resources[res1].value, 1)
        self.assertEqual(p.resources[res2].value, 0)

    def test_action_cost_insufficient(self) -> None:
        a = events.Action()

        res1 = creature.Resource()
        res2 = creature.Resource()

        rc1 = creature.ResourceCost()
        rc1.resource = res1
        rc1.cost = 1
        rc2 = creature.ResourceCost()
        rc2.resource = res2
        rc2.cost = 4
        a.costs = [rc1, rc2]
        a.event = events.InfoEvent()

        p = creature.Player()
        r1 = creature.CreatureResource()
        r1.value = 2
        r2 = creature.CreatureResource()
        r2.value = 3
        p.resources = {res1: r1, res2: r2}

        self.assertFalse(a.check_requirements(p))
        results = a.take(p)
        self.assertIsInstance(results[0].exception, creature.InsufficientResourceError)
        self.assertEqual(p.resources[res1].value, 2)
        self.assertEqual(p.resources[res2].value, 3)

    def test_action_requirement(self) -> None:
        a = events.Action()
        req = type('', (), {})
        req.meets = mock.Mock()
        req.assert_meets = mock.Mock()
        req.meets.return_value = False

        a.requirements = [req]
        p = mock.Mock()

        self.assertFalse(a.check_requirements(p))
        req.meets.return_value = True
        self.assertTrue(a.check_requirements(p))
        a.take(p)
        req.assert_meets.assert_called_once_with(p)

    def test_action_visibility(self) -> None:
        a = events.Action()
        req = type('', (), {})
        req.meets = mock.Mock()
        req.meets.return_value = False

        a.visibility = [req]
        p = creature.Player()
        p.base_actions = [a]
        p.location = type('', (), {})
        p.location.travel_actions = []
        p.location.local_actions = []

        req.meets.return_value = False
        self.assertListEqual(p.available_actions, [])

        req.meets.return_value = True
        self.assertListEqual(p.available_actions, [a])

    def test_skill_event(self) -> None:
        s = creature.Skill()
        p = creature.Player()
        ps = creature.CreatureSkill()
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

        p.events.register(e, **params)

        self.assertIs(p.events.fire_all()[0], sret)
        e.success.fire.assert_called_once_with(p, param=4)
        e.failure.assert_not_called()

        e.test.test.return_value = False
        e.success.reset_mock()
        e.failure.reset_mock()

        p.events.register(e, **params)

        self.assertIs(p.events.fire_all()[0], fret)
        e.success.assert_not_called()
        e.failure.fire.assert_called_once_with(p)

    def test_sequence_event(self) -> None:
        evs = [mock.Mock(), mock.Mock()]

        r1 = object()
        r2 = object()
        evs[0].fire = mock.Mock()
        evs[1].fire = mock.Mock()
        evs[0].fire.return_value = r1
        evs[1].fire.return_value = r2

        e = events.SequenceEvent()
        e.events = evs
        p = creature.Player()

        p.events.register(e)
        ret = p.events.fire_all()

        self.assertSequenceEqual(ret, [r1, r2])
        evs[0].fire.assert_called_once()
        evs[1].fire.assert_called_once()

    def test_cond_event(self) -> None:
        e = events.ConditionEvent()

        e.true = object()
        e.false = object()
        e.condition = mock.Mock()

        p = creature.Player()

        e.condition.meets.return_value = True
        e.fire(p)
        self.assertIs(p.events.events[0][0], e.true)

        p.events.events = []
        e.condition.meets.return_value = False
        e.fire(p)
        self.assertIs(p.events.events[0][0], e.false)

    def test_chance_event(self) -> None:
        e = events.ChanceEvent()

        r1 = object()
        r2 = object()

        e.if_ = mock.Mock()
        e.else_ = mock.Mock()
        e.if_.fire = mock.MagicMock(return_value=r1)
        e.else_.fire = mock.MagicMock(return_value=r2)

        e.randomizer = mock.MagicMock(return_value=0.1)
        p = creature.Player()

        p.events.register(e)
        ret = p.events.fire_all()

        self.assertSequenceEqual(ret, [r1])
        e.if_.fire.assert_called_once()
        e.else_.fire.assert_not_called()

    def test_chance_event_else(self) -> None:
        e = events.ChanceEvent()

        r1 = object()
        r2 = object()

        e.if_ = mock.Mock()
        e.else_ = mock.Mock()
        e.if_.fire = mock.MagicMock(return_value=r1)
        e.else_.fire = mock.MagicMock(return_value=r2)

        e.randomizer = mock.MagicMock(return_value=0.8)
        p = creature.Player()

        p.events.register(e)
        ret = p.events.fire_all()

        self.assertSequenceEqual(ret, [r2])
        e.if_.fire.assert_not_called()
        e.else_.fire.assert_called_once()

    def test_add_timed_bonus(self) -> None:
        c = mock.Mock()
        c.add_timed_bonus.return_value = None

        e = events.AddTimedBonusEvent()
        e.bonus = object()
        e.time = 2

        ret = e.fire(c)
        self.assertIs(ret.bonus, e.bonus)
        self.assertEqual(ret.time, e.time)

        c.add_timed_bonus.assert_called_once_with(e.bonus, e.time)


class TestStateMachineEvents(unittest.TestCase):
    def test_state_init_event(self) -> None:
        e = events.StateMachineInitEvent()
        p = mock.Mock()
        m = object()
        e.machine = m
        r = e.fire(p)
        p.enter_state_machine.assert_called_once_with(m)
        self.assertIs(r.machine, m)

    def test_state_exit_event(self) -> None:
        e = events.StateMachineExitEvent()
        p = mock.Mock()
        m = object()
        e.machine = m
        r = e.fire(p)
        p.exit_state_machine.assert_called_once_with(m)
        self.assertIs(r.machine, m)

    def test_state_requirement(self) -> None:
        sm = creature.PassiveStateMachine()
        s = creature.PassiveState()
        sm.initial = s

        p = creature.Player()

        r = events.StateRequirement()
        r.machine = sm

        self.assertTrue(r.meets(p))

        r.state = s
        self.assertFalse(r.meets(p))

        p.enter_state_machine(sm)
        self.assertTrue(r.meets(p))

        r.state = None
        self.assertFalse(r.meets(p))
