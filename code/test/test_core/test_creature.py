import unittest
from unittest import mock

import dtrpg.core.item as item
import dtrpg.core.map as map_
import dtrpg.core.creature as creature
import dtrpg.core.events as events


class TestPlayer(unittest.TestCase):
    def test_player_move(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()

        travel_action = map_.TravelAction()
        travel_action.to = loc2
        loc1.travel_actions = [travel_action]

        p = creature.Player()
        p.location = loc1

        e = travel_action.take(p)[0]

        self.assertIs(p.location, loc2)
        self.assertIs(e.from_, loc1)
        self.assertIs(e.to, loc2)
        self.assertIs(e.player, p)


class TestPlayerFactory(unittest.TestCase):
    def test_player_factory(self) -> None:
        factory = creature.PlayerFactory()
        loc = map_.Location()
        cf = item.ContainerFactory()

        factory.default_location = loc
        factory.container_factory = cf

        p = factory.create()

        self.assertIs(p.location, loc)
        self.assertIsInstance(p.items, item.Container)

    def test_player_factory_resources(self) -> None:
        factory = creature.PlayerFactory()
        rf = creature.CreatureResourceFactory()
        res = creature.Resource()
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
        factory = creature.CreatureResourceFactory()
        res = creature.Resource()
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
        r = creature.CreatureResource()
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

        r = creature.CreatureResource()
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

        r = creature.CreatureResource()
        r.value = 10
        r.max = 12
        r.base_gen_rate = 0.5
        r.clock = clock

        self.assertEqual(r.value, 12)
        self.assertEqual(r.value, 12)
        self.assertEqual(r.value, 12)
        r.value = 5
        self.assertEqual(r.value, 7)

    def test_killed(self) -> None:
        r = creature.Resource()
        r.vital = True
        cr = creature.CreatureResource()
        cr.value = 1

        c = creature.Fighter()
        c.resources = {r: cr}

        self.assertFalse(c.killed)
        cr.value = 0
        self.assertTrue(c.killed)

    def test_killed_no_vital(self) -> None:
        r = creature.Resource()
        r.vital = False
        cr = creature.CreatureResource()
        cr.value = 1

        c = creature.Fighter()
        c.resources = {r: cr}

        self.assertFalse(c.killed)
        cr.value = 0
        self.assertFalse(c.killed)

    def test_resource_change_add(self) -> None:
        cr = creature.CreatureResource()
        cr.value = 1
        r = creature.Resource()
        c = creature.ResourceChange()
        c.value = 2
        c.resource = r

        crt = creature.Creature()
        crt.resources = {r: cr}

        c.apply(crt)

        self.assertEqual(cr.value, 3)

    def test_resource_change_set(self) -> None:
        cr = creature.CreatureResource()
        cr.value = 1
        r = creature.Resource()
        c = creature.ResourceChange()
        c.value = 2
        c.resource = r
        c.op = creature.ResourceChangeOp.SET

        crt = creature.Creature()
        crt.resources = {r: cr}

        c.apply(crt)

        self.assertEqual(cr.value, 2)

    def test_resource_set_below_0(self) -> None:
        r = creature.Resource()
        r.vital = True
        cr = creature.CreatureResource()
        cr.value = -10

        self.assertEqual(cr.value, 0)


class TestSkill(unittest.TestCase):
    def test_player_skill(self) -> None:
        s1 = creature.Skill()
        f1 = creature.CreatureSkillFactory()
        f1.initial = 2
        f1.skill = s1

        s2 = creature.Skill()
        f2 = creature.CreatureSkillFactory()
        f2.initial = 4
        f2.skill = s2

        pf = creature.PlayerFactory()
        pf.skill_factories = [f1, f2]
        pf.container_factory = mock.Mock()
        pf.container_factory.create.return_value = None

        p = pf.create()

        self.assertEqual(p.skills[s1].value, 2)
        self.assertEqual(p.skills[s1].skill, s1)
        self.assertEqual(p.skills[s2].value, 4)
        self.assertEqual(p.skills[s2].skill, s2)

    def test_skill_experience(self) -> None:
        s1 = creature.Skill()
        s1.experience_from_test = "difficulty if success else level"
        s1.progression = "level**2"

        f1 = creature.CreatureSkillFactory()
        f1.skill = s1

        pf = creature.PlayerFactory()
        pf.skill_factories = [f1]
        pf.container_factory = mock.Mock()
        pf.container_factory.create.return_value = None

        p = pf.create()

        self.assertEqual(p.skills[s1]._experience, 0)
        self.assertEqual(p.skills[s1].value, 1)

        p.skills[s1].add_experience(1)

        self.assertEqual(p.skills[s1]._experience, 1)
        self.assertEqual(p.skills[s1].value, 2)

        st = creature.SkillTest()
        st.skill = s1
        st.difficulty = 3
        st.tester = mock.Mock()

        st.tester.test.return_value = False

        self.assertFalse(st.test(p))
        st.tester.test.assert_called_once_with(2, 3)

        self.assertEqual(p.skills[s1]._experience, 3)
        self.assertEqual(p.skills[s1].value, 2)

        st.tester.test.return_value = True

        self.assertTrue(st.test(p))
        st.tester.test.assert_called_with(2, 3)

        self.assertEqual(p.skills[s1]._experience, 6)
        self.assertEqual(p.skills[s1].value, 3)


class TestStatistic(unittest.TestCase):
    def test_statistic_base(self) -> None:
        c = creature.Creature()
        s = creature.Statistic()
        cs = creature.CreatureStatistic(s, 2)
        c.statistics.statistics = {s: cs}

        self.assertEqual(c.statistics[s], 2)

    def test_statistic_with_item_bonus(self) -> None:
        c = creature.Creature()
        s = creature.Statistic()
        cs = creature.CreatureStatistic(s, 2)
        c.statistics.statistics = {s: cs}

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1
        i.statistic_bonuses[s] = 3

        c.item_slots = {slot1: i, slot2: None}

        self.assertEqual(c.statistics[s], 5)


class TestStatisticFactory(unittest.TestCase):
    def test_statistic_factory_base(self) -> None:
        ff = creature.PlayerFactory()
        ff.container_factory = mock.Mock()
        sf = creature.StatisticFactory()
        s = creature.Statistic()
        sf.statistic = s
        sf.base = 3
        ff.statistic_factories = [sf]

        f = ff.create()

        self.assertEqual(f.statistics[s], 3)


class TestItemSlot(unittest.TestCase):
    def test_item_slot_equip(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: None, slot2: None}
        c.items = item.Container()
        c.items.add(item.ItemStack(i, 1))

        c.equip(i)

        self.assertIs(c.item_slots[slot1], i)
        self.assertEqual(c.items.count(i), 0)

    def test_item_slot_equip_not_equippable(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()

        c.item_slots = {slot1: None, slot2: None}
        c.items = item.Container()
        c.items.add(item.ItemStack(i, 1))

        self.assertRaises(item.NotEquippableException, lambda: c.equip(i))

    def test_item_slot_equip_slot_taken(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i2 = item.Item()
        i.slot = slot1
        i2.slot = slot1

        c.item_slots = {slot1: i2, slot2: None}
        c.items = item.Container()
        c.items.add(item.ItemStack(i, 1))

        c.equip(i)

        self.assertIs(c.item_slots[slot1], i)
        self.assertEqual(c.items.count(i), 0)
        self.assertEqual(c.items.count(i2), 1)

    def test_item_slot_unequip(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: i, slot2: None}
        c.items = item.Container()

        c.unequip(i)

        self.assertIs(c.item_slots[slot1], None)
        self.assertEqual(c.items.count(i), 1)

    def test_item_slot_unequip_not_equipped(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: None, slot2: None}
        c.items = item.Container()

        self.assertRaises(item.ItemNotEquippedException, lambda: c.unequip(i))

    def test_item_slot_unequip_container_full(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i2 = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: i, slot2: None}
        c.items = item.Container()
        c.items.max_items = 1
        c.items.add(item.ItemStack(i2, 1))

        self.assertRaises(item.ContainerOverflowException, lambda: c.unequip(i))

    def test_item_unequip_slot(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: i, slot2: None}
        c.items = item.Container()

        c.unequip_slot(slot1)

        self.assertIs(c.item_slots[slot1], None)
        self.assertEqual(c.items.count(i), 1)

    def test_item_unequip_slot_not_equipped(self) -> None:
        c = creature.Creature()

        slot1 = item.ItemSlot()
        slot2 = item.ItemSlot()

        i = item.Item()
        i.slot = slot1

        c.item_slots = {slot1: i, slot2: None}
        c.items = item.Container()

        self.assertRaises(item.SlotNotEquippedException, lambda: c.unequip_slot(slot2))


class TestFighter(unittest.TestCase):
    def test_attack(self):
        c = creature.Fighter()
        a1 = object()
        a2 = object()

        slot = item.ItemSlot()
        i = item.Item()
        i.slot = slot
        i.attack = a2

        c.item_slots = {slot: None}

        c.default_attack = a1
        self.assertIs(c.attack, a1)

        c.item_slots[slot] = i
        self.assertIs(c.attack, a2)


class TestStateMachine(unittest.TestCase):
    def test_machine_init(self):
        p = creature.Player()

        m = creature.ActiveStateMachine()
        s = creature.State()
        m.initial = s

        p.enter_state_machine(m)

        self.assertTupleEqual(p.active_state, (s, m))

    def test_machine_exit(self):
        p = creature.Player()

        m = creature.ActiveStateMachine()
        s = creature.State()
        m.initial = s

        m2 = creature.ActiveStateMachine()
        s2 = creature.State()
        m2.initial = s2

        p.enter_state_machine(m)
        p.enter_state_machine(m2)

        self.assertTupleEqual(p.active_state, (s2, m2))
        p.exit_state_machine(m2)
        self.assertTupleEqual(p.active_state, (s, m))
        p.exit_state_machine(m)
        self.assertTupleEqual(p.active_state, (None, None))

    def test_state_transition(self):
        p = creature.Player()

        m = creature.ActiveStateMachine()
        s = creature.State()
        s2 = creature.State()
        m.initial = s
        s.machine = m
        s2.machine = m
        t = creature.StateTransition()
        t2 = creature.StateTransition()
        t.event = object()
        t.to = s2

        e = object()
        e2 = object()

        s.transitions = {e: t, e2: t2}

        p.enter_state_machine(m)
        p.on_event(e2)

        self.assertTupleEqual(p.active_state, (s, m))

        p.on_event(e)

        self.assertTupleEqual(p.active_state, (s2, m))
        self.assertSequenceEqual(p.events.events, [(t.event, {})])

    def test_avaliable_actions(self):
        p = creature.Player()

        m = creature.ActiveStateMachine()
        s = creature.ActiveState()
        m.initial = s

        g1 = object()
        g2 = object()

        m.allowed_action_groups = [g1]

        a1 = events.Action()
        a2 = events.Action()
        a3 = events.Action()
        a4 = events.Action()
        a5 = events.Action()

        s.actions = [a5]

        a1.groups = []
        a2.groups = [g1]
        a3.groups = [g2]
        a4.groups = [g1, g2]

        p.base_actions = [a1, a2, a3, a4]
        p.location = mock.Mock()
        p.location.travel_actions = []
        p.location.local_actions = []

        self.assertSequenceEqual(p.available_actions, [a1, a2, a3, a4])
        p.enter_state_machine(m)
        self.assertSequenceEqual(p.available_actions, [a2, a4, a5])

    def test_passive_machine_init(self):
        p = creature.Player()

        m = creature.PassiveStateMachine()
        s = creature.State()
        m.initial = s

        p.enter_state_machine(m)

        self.assertIs(p.passive_state(m), s)

    def test_passive_machine_exit(self):
        p = creature.Player()

        m = creature.PassiveStateMachine()
        s = creature.State()
        m.initial = s

        p.enter_state_machine(m)
        p.exit_state_machine(m)
        self.assertIs(p.passive_state(m), None)

    def test_passive_state_transition(self):
        p = creature.Player()

        m = creature.PassiveStateMachine()
        s = creature.State()
        s.machine = m
        s2 = creature.State()
        s2.machine = m
        m.initial = s
        t = creature.StateTransition()
        t2 = creature.StateTransition()
        t.event = object()
        t.to = s2

        e = object()
        e2 = object()

        s.transitions = {e: t, e2: t2}

        p.enter_state_machine(m)
        p.on_event(e2)

        self.assertIs(p.passive_state(m), s)

        p.on_event(e)

        self.assertIs(p.passive_state(m), s2)
        self.assertSequenceEqual(p.events.events, [(t.event, {})])

    def test_invalid_action_event(self):
        p = creature.Player()
        p.default_invalid_action_event = object()

        self.assertIs(p.invalid_action_event, p.default_invalid_action_event)

        m = creature.ActiveStateMachine()
        s = creature.State()

        m.initial = s

        p.enter_state_machine(m)

        self.assertIs(p.invalid_action_event, p.default_invalid_action_event)

        m.invalid_action_event = object()
        self.assertIs(p.invalid_action_event, m.invalid_action_event)
