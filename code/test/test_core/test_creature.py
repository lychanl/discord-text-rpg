import unittest
from unittest import mock

import dtrpg.core.item as item
import dtrpg.core.map as map_
import dtrpg.core.creature as creature


class TestPlayer(unittest.TestCase):
    def test_player_move(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()

        travel_action = map_.TravelAction()
        travel_action.to = loc2
        loc1.travel_actions = [travel_action]

        p = creature.Player()
        p.location = loc1

        e = travel_action.take(p)

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
