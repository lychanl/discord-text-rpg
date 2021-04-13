import unittest
from unittest import mock

import dtrpg.core.fighting as f
import dtrpg.core.creature as c


class TestFightMoving(unittest.TestCase):
    def test_melee_into_melee(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.MELEE}, {f2: f.MoveDestination.MELEE}, {})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(r1), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f1})
        self.assertSetEqual(m2, {f2})

    def test_ranged_into_melee(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.MELEE}, {}, {}, {f2: f.MoveDestination.MELEE})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(r1), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f1})
        self.assertSetEqual(m2, {f2})

    def test_melee_into_ranged(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.RANGED}, {f2: f.MoveDestination.RANGED}, {})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})

    def test_ranged_into_ranged(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.RANGED}, {}, {}, {f2: f.MoveDestination.RANGED})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})
        self.assertSetEqual(
            set(), {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_melee_both_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.FLEE}, {f2: f.MoveDestination.FLEE}, {})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})
        self.assertSetEqual(
            {
                (f1, f.MoveDestination.MELEE, f.MoveDestination.RANGED),
                (f2, f.MoveDestination.MELEE, f.MoveDestination.RANGED)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_ranged_both_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.FLEE}, {}, {}, {f2: f.MoveDestination.FLEE})

        self.assertEqual(len(r1), 0)
        self.assertEqual(len(r2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(fl1, {f1})
        self.assertSetEqual(fl2, {f2})
        self.assertSetEqual(
            {
                (f1, f.MoveDestination.RANGED, f.MoveDestination.FLEE),
                (f2, f.MoveDestination.RANGED, f.MoveDestination.FLEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_melee_one_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        e.move_test.test = mock.Mock()
        e.move_test.test.return_value = True

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.MELEE}, {f2: f.MoveDestination.FLEE}, {})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(r1), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f1})
        self.assertSetEqual(m2, {f2})
        self.assertSetEqual(
            set(), {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

        e.move_test.test.reset_mock()
        e.move_test.test.return_value = False

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.MELEE}, {f2: f.MoveDestination.FLEE}, {})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})
        self.assertSetEqual(
            {
                (f1, f.MoveDestination.MELEE, f.MoveDestination.RANGED),
                (f2, f.MoveDestination.MELEE, f.MoveDestination.RANGED)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_melee_one_ranged_one_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {}, {f1: f.MoveDestination.RANGED}, {f2: f.MoveDestination.FLEE}, {})

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})

    def test_ranged_one_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        e.move_test.test = mock.Mock()
        e.move_test.test.return_value = True

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.RANGED}, {}, {}, {f2: f.MoveDestination.FLEE})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(r2, {f2})
        self.assertSetEqual(
            set(),
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

        e.move_test.test.reset_mock()
        e.move_test.test.return_value = False

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.RANGED}, {}, {}, {f2: f.MoveDestination.FLEE})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(r2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(fl2, {f2})
        self.assertSetEqual(
            {
                (f2, f.MoveDestination.RANGED, f.MoveDestination.FLEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_ranged_one_melee_one_escaping(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()

        e = f.FightEngine()
        e.move_test.test = mock.Mock()
        e.move_test.test.return_value = True

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.MELEE}, {}, {}, {f2: f.MoveDestination.FLEE})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(r1), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f1})
        self.assertSetEqual(m2, {f2})
        self.assertSetEqual(
            {
                (f1, f.MoveDestination.RANGED, f.MoveDestination.MELEE),
                (f2, f.MoveDestination.RANGED, f.MoveDestination.MELEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

        e.move_test.test.reset_mock()
        e.move_test.test.return_value = False

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves(
            {f1: f.MoveDestination.MELEE}, {}, {}, {f2: f.MoveDestination.FLEE})

        e.move_test.test.assert_called_once_with(f1, f2)

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(r2), 0)
        self.assertEqual(len(m1), 0)
        self.assertEqual(len(m2), 0)
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(fl2, {f2})
        self.assertSetEqual(
            {
                (f2, f.MoveDestination.RANGED, f.MoveDestination.FLEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_multiple_some_melee(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        e = f.FightEngine()

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves({
            f1: f.MoveDestination.RANGED, f2: f.MoveDestination.MELEE
        }, {}, {}, {
            f3: f.MoveDestination.FLEE, f4: f.MoveDestination.MELEE
        })

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f2})
        self.assertSetEqual(m2, {f4})
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(fl2, {f3})
        self.assertSetEqual(
            {
                (f2, f.MoveDestination.RANGED, f.MoveDestination.MELEE),
                (f3, f.MoveDestination.RANGED, f.MoveDestination.FLEE),
                (f4, f.MoveDestination.RANGED, f.MoveDestination.MELEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

    def test_multiple_escape(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        e = f.FightEngine()
        e.move_test.test = mock.Mock()
        e.move_test.test.return_value = True

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves({
            f1: f.MoveDestination.RANGED, f2: f.MoveDestination.MELEE
        }, {}, {}, {
            f3: f.MoveDestination.FLEE, f4: f.MoveDestination.FLEE
        })

        e.move_test.test.assert_has_calls([
            mock.call(f1, f3), mock.call(f2, f3), mock.call(f1, f4), mock.call(f2, f4)
        ])

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(fl2), 0)
        self.assertEqual(len(r2), 0)
        self.assertSetEqual(m1, {f2})
        self.assertSetEqual(m2, {f3, f4})
        self.assertSetEqual(r1, {f1})
        self.assertSetEqual(
            {
                (f2, f.MoveDestination.RANGED, f.MoveDestination.MELEE),
                (f3, f.MoveDestination.RANGED, f.MoveDestination.MELEE),
                (f4, f.MoveDestination.RANGED, f.MoveDestination.MELEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )

        e.move_test.test.reset_mock()
        e.move_test.test.return_value = False

        fl1, r1, m1, m2, r2, fl2, events = e._make_moves({
            f1: f.MoveDestination.RANGED, f2: f.MoveDestination.MELEE
        }, {}, {}, {
            f3: f.MoveDestination.FLEE, f4: f.MoveDestination.FLEE
        })

        e.move_test.test.assert_has_calls([
            mock.call(f1, f3), mock.call(f2, f3), mock.call(f1, f4), mock.call(f2, f4)
        ])

        self.assertEqual(len(fl1), 0)
        self.assertEqual(len(m2), 0)
        self.assertEqual(len(r2), 0)
        self.assertEqual(len(m1), 0)
        self.assertSetEqual(r1, {f1, f2})
        self.assertSetEqual(fl2, {f3, f4})
        self.assertSetEqual(
            {
                (f3, f.MoveDestination.RANGED, f.MoveDestination.FLEE),
                (f4, f.MoveDestination.RANGED, f.MoveDestination.FLEE)
            },
            {(e.fighter, e.from_loc, e.to_loc) for e in events}
        )


class TestTactic(unittest.TestCase):
    def test_status(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        health = c.Resource()

        f1.resources[health] = c.CreatureResource()
        f1.resources[health].max = 4
        f1.resources[health].value = 2

        f2.resources[health] = c.CreatureResource()
        f2.resources[health].max = 4
        f2.resources[health].value = 1

        f3.resources[health] = c.CreatureResource()
        f3.resources[health].max = 4
        f3.resources[health].value = 3

        f4.resources[health] = c.CreatureResource()
        f4.resources[health].max = 4
        f4.resources[health].value = 4

        e = f.FightEngine()
        e.health = health

        status = e._prepare_status({f1}, {f2, f3}, {f4}, {})

        self.assertListEqual(status.fighters, [{
            f1: {f.StatusFlag.RANGED, f.StatusFlag.LOW_HEALTH},
            f2: {f.StatusFlag.MELEE, f.StatusFlag.LOW_HEALTH},
            f3: {f.StatusFlag.MELEE, f.StatusFlag.HIGH_HEALTH}
        }, {
            f4: {f.StatusFlag.MELEE, f.StatusFlag.FULL_HEALTH}
        }])

        self.assertDictEqual(status.allies(f1), {
            f2: {f.StatusFlag.MELEE, f.StatusFlag.LOW_HEALTH},
            f3: {f.StatusFlag.MELEE, f.StatusFlag.HIGH_HEALTH}
        })
        self.assertDictEqual(status.allies(f4), {})
        self.assertSetEqual(status[f1], {f.StatusFlag.RANGED, f.StatusFlag.LOW_HEALTH})

    def test_tactic_condition(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        s = f.FightStatus([{
            f1: {f.StatusFlag.RANGED, f.StatusFlag.LOW_HEALTH},
            f2: {f.StatusFlag.MELEE, f.StatusFlag.LOW_HEALTH},
            f3: {f.StatusFlag.MELEE, f.StatusFlag.HIGH_HEALTH}
        }, {
            f4: {f.StatusFlag.MELEE, f.StatusFlag.FULL_HEALTH}
        }])

        t = f.TacticCondition()

        t.quantifier = f.TacticQuantifier.ALL_ENEMIES
        t.condition = f.StatusFlag.MELEE

        self.assertTrue(t.check(f1, s))
        self.assertFalse(t.check(f4, s))

        t.quantifier = f.TacticQuantifier.ANY_ENEMY
        t.condition = f.StatusFlag.RANGED

        self.assertFalse(t.check(f1, s))
        self.assertTrue(t.check(f4, s))

        t.quantifier = f.TacticQuantifier.ANY_ALLY
        t.condition = f.StatusFlag.RANGED

        self.assertTrue(t.check(f2, s))
        self.assertFalse(t.check(f4, s))
        self.assertFalse(t.check(f1, s))

        t.quantifier = f.TacticQuantifier.ALL_ALLIES
        t.condition = f.StatusFlag.MELEE

        self.assertTrue(t.check(f1, s))
        self.assertTrue(t.check(f4, s))
        self.assertFalse(t.check(f2, s))

        t.quantifier = f.TacticQuantifier.SELF
        t.condition = f.StatusFlag.MELEE

        self.assertFalse(t.check(f1, s))
        self.assertTrue(t.check(f4, s))

    def test_tactic_predicate(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        s = f.FightStatus([{
            f1: {f.StatusFlag.RANGED, f.StatusFlag.LOW_HEALTH},
            f2: {f.StatusFlag.MELEE, f.StatusFlag.LOW_HEALTH},
            f3: {f.StatusFlag.MELEE, f.StatusFlag.HIGH_HEALTH}
        }, {
            f4: {f.StatusFlag.MELEE, f.StatusFlag.FULL_HEALTH}
        }])

        c1 = f.TacticCondition()
        c1.quantifier = f.TacticQuantifier.ALL_ALLIES
        c1.condition = f.StatusFlag.MELEE

        c2 = f.TacticCondition()
        c2.quantifier = f.TacticQuantifier.SELF
        c2.condition = f.StatusFlag.RANGED

        p = f.MovePredicate()
        p.conditions = [c1, c2]
        p.result = mock.Mock()
        p.result.can_take.return_value = True

        self.assertTrue(p.check(f1, s))
        self.assertFalse(p.check(f2, s))
        self.assertFalse(p.check(f4, s))

        p.result.can_take.return_value = False

        self.assertFalse(p.check(f1, s))

    def test_tactic(self) -> None:
        tactic = f.Tactic()
        tactic.move_predicates = [mock.Mock(), mock.Mock(), mock.Mock()]
        tactic.move_predicates[0].check.return_value = False
        tactic.move_predicates[0].result = 1
        tactic.move_predicates[1].check.return_value = True
        tactic.move_predicates[1].result = 2
        tactic.move_predicates[2].check.return_value = False
        tactic.move_predicates[2].result = 3

        self.assertEqual(tactic.get_move(None, None), 2)


class TestFightingActions(unittest.TestCase):
    def test_target_priority(self) -> None:
        f1 = c.Fighter()
        f2 = c.Fighter()
        f3 = c.Fighter()
        f4 = c.Fighter()

        s = f.FightStatus([{
            f1: {f.StatusFlag.RANGED, f.StatusFlag.LOW_HEALTH},
            f2: {f.StatusFlag.MELEE, f.StatusFlag.LOW_HEALTH},
            f3: {f.StatusFlag.MELEE, f.StatusFlag.HIGH_HEALTH}
        }, {
            f4: {f.StatusFlag.MELEE, f.StatusFlag.FULL_HEALTH}
        }])

        a = f.TargetedAction()

        a.allow_target_self = mock.Mock(return_value=False)
        a.allow_target_ally = mock.Mock(return_value=False)
        a.allow_target_enemy = mock.Mock(return_value=True)
        a.allow_ranged_range = mock.Mock(return_value=False)
        a.allow_melee_range = mock.Mock(return_value=True)

        self.assertSetEqual(a.get_possible_targets(f1, s), {f4})
        self.assertSetEqual(a.get_possible_targets(f4, s), {f2, f3})

    def test_attack(self) -> None:
        f1 = mock.Mock()
        f2 = c.Fighter()

        attack_skill = c.Skill()
        attack_cskill = c.CreatureSkill()
        attack_cskill.skill = attack_skill

        evasion_skill = c.Skill()
        evasion_cskill = c.CreatureSkill()
        evasion_cskill.skill = evasion_skill

        f1.skills = {attack_skill: attack_cskill}
        f2.skills = {evasion_skill: evasion_cskill}

        f1.attack = f.Attack()
        f1.attack.attacks_number = 3
        f1.attack.ranged = True
        f1.attack.hit_skill = attack_skill
        f1.attack.hit_skill_modifier = 2
        f1.attack.evasion_skill = evasion_skill
        f1.attack.evasion_skill_modifier = 1
        f1.attack.on_hit = mock.Mock()
        f1.attack.on_hit.fire.return_value = 1
        f1.attack.on_miss = mock.Mock()
        f1.attack.on_miss.fire.return_value = 2
        f1.attack.tester = mock.Mock()
        f1.attack.tester.test.side_effect = [True, False, True]

        action = f.AttackAction()

        result = action.apply(f1, f2)
        self.assertListEqual(result.results, [1, 2, 1])
        f1.attack.tester.test.assert_called_with(1 + 2, 1 + 1)

    def test_damage(self) -> None:
        f1 = mock.Mock()
        f2 = c.Fighter()

        health = c.Resource()
        f1.resources = {health: c.CreatureResource()}
        f1.resources[health].max = 5
        f1.resources[health].value = 5

        armor = c.Statistic()

        f1.statistics = {armor: 3}

        d = f.Damage()
        d.damage_tests_number = 3
        d.damage_test_mod = 4
        d.damage_per_hit = 2

        d.damaged_resource = health
        d.armor = armor

        d.tester = mock.Mock()
        d.tester.test.side_effect = [True, False, True]

        result = d.fire(f2, target=f1)

        d.tester.test.assert_has_calls([
            mock.call(4, 3),
            mock.call(4, 3),
            mock.call(4, 3)
        ])
        self.assertEqual(result.damage_dealt, 4)
        self.assertEqual(f1.resources[health].value, 1)


class TestFightEvent(unittest.TestCase):
    def test_fight_event_victory(self) -> None:
        fighter = c.Player()
        enemy_factory = mock.Mock()
        enemy = mock.Mock()
        enemy_factory.create.return_value = enemy
        enemy.killed = True
        lr = object()
        enemy.loot_events = [mock.Mock()]
        enemy.loot_events[0].fire.return_value = lr

        e = f.FightEvent()
        e.victory = mock.Mock()
        vr = object()
        e.victory.fire.return_value = vr
        e.enemy_factories = [enemy_factory]
        e.fight_engine = mock.Mock()
        e.fight_engine.fight.return_value = f.FightResult.GROUP1, [], {}, {}

        fighter.events.register(e)
        r, loot, nxt, = fighter.events.fire_all()

        enemy_factory.create.assert_called_once()
        self.assertListEqual(r.group1, [fighter])
        self.assertListEqual(r.group2, [enemy])
        self.assertEqual(r.result, f.FightResult.GROUP1)
        self.assertEqual(nxt, vr)
        self.assertEqual(loot, lr)

        e.victory.fire.assert_called_once()
        e.fight_engine.fight.assert_called_once_with([fighter], [enemy])
        enemy.loot_events[0].fire.assert_called_once_with(fighter)

    def test_fight_event_defeat(self) -> None:
        fighter = c.Player()
        fighter.on_killed = mock.Mock()
        fighter.on_killed.fire = mock.Mock()
        enemy_factory = mock.Mock()
        enemy = object()
        enemy_factory.create.return_value = enemy

        e = f.FightEvent()
        e.defeat = mock.Mock()
        dr = object()
        e.defeat.fire.return_value = dr
        e.enemy_factories = [enemy_factory]
        e.fight_engine = mock.Mock()
        e.fight_engine.fight.return_value = f.FightResult.GROUP2, [], {}, {}

        fighter.events.register(e)
        r, nxt, = fighter.events.fire_all()

        enemy_factory.create.assert_called_once()
        self.assertListEqual(r.group1, [fighter])
        self.assertListEqual(r.group2, [enemy])
        self.assertEqual(r.result, f.FightResult.GROUP2)
        self.assertEqual(nxt, dr)

        e.defeat.fire.assert_called_once()
        e.fight_engine.fight.assert_called_once_with([fighter], [enemy])
        fighter.on_killed.assert_not_called()

    def test_fight_event_defeat_killed(self) -> None:
        fighter = c.Player()
        fighter.on_killed = mock.Mock()
        fighter.on_killed.fire = mock.Mock()
        okr = object()
        fighter.on_killed.fire.return_value = okr
        enemy_factory = mock.Mock()
        enemy = object()
        enemy_factory.create.return_value = enemy

        e = f.FightEvent()
        e.defeat = mock.Mock()
        dr = object()
        e.defeat.fire.return_value = dr
        e.enemy_factories = [enemy_factory]
        e.fight_engine = mock.Mock()
        e.fight_engine.fight.return_value = f.FightResult.GROUP2, [], {fighter}, {}

        fighter.events.register(e)
        r, nxt, killed = fighter.events.fire_all()

        enemy_factory.create.assert_called_once()
        self.assertListEqual(r.group1, [fighter])
        self.assertListEqual(r.group2, [enemy])
        self.assertEqual(r.result, f.FightResult.GROUP2)
        self.assertEqual(nxt, dr)
        self.assertEqual(killed, okr)

        e.defeat.fire.assert_called_once()
        e.fight_engine.fight.assert_called_once_with([fighter], [enemy])
        fighter.on_killed.fire.assert_called_once_with(fighter)

    def test_fight_event_draw(self) -> None:
        fighter = c.Player()
        enemy_factory = mock.Mock()
        enemy = object()
        enemy_factory.create.return_value = enemy

        e = f.FightEvent()
        e.draw = mock.Mock()
        dr = object()
        e.draw.fire.return_value = dr
        e.enemy_factories = [enemy_factory]
        e.fight_engine = mock.Mock()
        e.fight_engine.fight.return_value = f.FightResult.DRAW, [], {}, {}

        fighter.events.register(e)
        r, nxt, = fighter.events.fire_all()

        enemy_factory.create.assert_called_once()
        self.assertListEqual(r.group1, [fighter])
        self.assertListEqual(r.group2, [enemy])
        self.assertEqual(r.result, f.FightResult.DRAW)
        self.assertEqual(nxt, dr)

        e.draw.fire.assert_called_once()
        e.fight_engine.fight.assert_called_once_with([fighter], [enemy])
