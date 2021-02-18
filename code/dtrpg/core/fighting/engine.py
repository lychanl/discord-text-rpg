from dtrpg.core.creature.skill import Skill, OpposedSkillTest

from enum import Enum

from typing import Dict, Tuple, Mapping, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.tester import SkillTester
    from dtrpg.core.creature.creature import Fighter


class StatusFlag(Enum):
    MELEE = 0
    RANGED = 1
    LOW_HEALTH = 2
    HIGH_HEALTH = 3
    FULL_HEALTH = 4


class MoveDestination(Enum):
    MELEE = 0
    RANGED = 1
    FLEE = 2

    def can_take(self, *args: Iterable, **kwargs: dict) -> bool:
        return True


class FightResult(Enum):
    GROUP1 = 1
    GROUP2 = 2
    DRAW = 3


class FightStatus:
    def __init__(
            self,
            groups: Tuple[Mapping['Fighter', Iterable[StatusFlag]], Mapping['Fighter', Iterable[StatusFlag]]]):
        self.fighters = groups

    def allies(self, fighter: 'Fighter') -> Mapping['Fighter', Iterable[StatusFlag]]:
        group = self.fighters[0] if fighter in self.fighters[0] else self.fighters[1]
        return {f: flags for f, flags in group.items() if f is not fighter}

    def enemies(self, fighter: 'Fighter') -> Mapping['Fighter', Iterable[StatusFlag]]:
        if fighter in self.fighters[0]:
            return self.fighters[1]
        return self.fighters[0]

    def __getitem__(self, fighter: 'Fighter') -> Iterable[StatusFlag]:
        for group in self.fighters:
            if fighter in group:
                return group[fighter]
        raise KeyError


class FightEngine:
    def __init__(self):
        self.health = None
        self.health_low_threshold = 0.5
        self.move_test = OpposedSkillTest()
        self.time_limit = 100

    @property
    def move_tester(self) -> 'SkillTester':
        return self.move_test.tester

    @move_tester.setter
    def move_tester(self, tester: 'SkillTester') -> None:
        self.move_test.tester = tester

    @property
    def speed_skill(self) -> 'Skill':
        return self.move_test.skill

    @speed_skill.setter
    def speed_skill(self, skill: 'Skill') -> None:
        self.move_test.skill = skill
        self.move_test.versus_skill = skill

    def fight(self, group1: Iterable['Fighter'], group2: Iterable['Fighter']) -> FightResult:
        ranged1 = set(group1)
        melee1 = set()
        melee2 = set()
        ranged2 = set(group2)

        for t in range(self.time_limit):
            status = self._prepare_status(ranged1, melee1, melee2, ranged2)

            ranged1_moves = {f: f.tactic.get_move(f, status) for f in ranged1}
            melee1_moves = {f: f.tactic.get_move(f, status) for f in melee1}
            melee2_moves = {f: f.tactic.get_move(f, status) for f in melee2}
            ranged2_moves = {f: f.tactic.get_move(f, status) for f in ranged2}

            flee1, ranged1, melee1, melee2, ranged2, flee2 = self._make_moves(
                ranged1_moves, melee1_moves, melee2_moves, ranged2_moves)

            # TODO move events

            if len(ranged1) + len(melee1) == 0 or len(ranged2) + len(melee2) == 0:
                break

            status = self._prepare_status(ranged1, melee1, melee2, ranged2)

            actions = {f: f.tactic.get_action(f, status) for f in ranged1 | melee1 | melee2 | ranged2}
            for f, (a, kwargs) in actions.items():
                a.apply(f, **kwargs)

            ranged1, defeated_r1 = self._check_defeats(ranged1)
            melee1, defeated_m1 = self._check_defeats(melee1)
            melee2, defeated_m2 = self._check_defeats(melee2)
            ranged2, defeated_r2 = self._check_defeats(ranged2)

            # TODO defeat events

            if len(ranged1) + len(melee1) == 0 or len(ranged2) + len(melee2) == 0:
                break

        if len(ranged1) + len(melee1) > 0 and len(ranged2) + len(melee2) == 0:
            return FightResult.GROUP1

        if len(ranged1) + len(melee1) == 0 and len(ranged2) + len(melee2) > 0:
            return FightResult.GROUP2

        return FightResult.DRAW

    def _prepare_status(
            self,
            ranged1: Iterable['Fighter'], melee1: Iterable['Fighter'],
            melee2: Iterable['Fighter'], ranged2: Iterable['Fighter']) -> FightStatus:
        group1 = {f: self._get_flags(f) | {StatusFlag.RANGED} for f in ranged1}
        group1.update({f: self._get_flags(f) | {StatusFlag.MELEE} for f in melee1})
        group2 = {f: self._get_flags(f) | {StatusFlag.RANGED} for f in ranged2}
        group2.update({f: self._get_flags(f) | {StatusFlag.MELEE} for f in melee2})
        return FightStatus([group1, group2])

    def _get_flags(self, fighter: 'Fighter') -> Iterable[StatusFlag]:
        return {
            self._get_health_flag(fighter)
        }

    def _get_health_flag(self, fighter: 'Fighter') -> StatusFlag:
        health = fighter.resources[self.health]
        if health.max is None:
            return StatusFlag.HIGH_HEALTH
        if health.max <= health.value:
            return StatusFlag.FULL_HEALTH
        if health.max * self.health_low_threshold < health.value:
            return StatusFlag.HIGH_HEALTH
        return StatusFlag.LOW_HEALTH

    def _make_moves(
            self,
            ranged1: Dict['Fighter', MoveDestination], melee1: Dict['Fighter', MoveDestination],
            melee2: Dict['Fighter', MoveDestination], ranged2: Dict['Fighter', MoveDestination]
    ) -> Tuple[Iterable['Fighter'], Iterable['Fighter'], Iterable['Fighter'],
               Iterable['Fighter'], Iterable['Fighter'], Iterable['Fighter']]:
        moves1 = dict(ranged1)
        moves1.update({
            f: move if move is not MoveDestination.FLEE else MoveDestination.RANGED for f, move in melee1.items()
        })
        moves2 = dict(ranged2)
        moves2.update({
            f: move if move is not MoveDestination.FLEE else MoveDestination.RANGED for f, move in melee2.items()
        })

        new_ranged1, new_melee1, fleeing1 = set(), set(), set()
        new_ranged2, new_melee2, fleeing2 = set(), set(), set()

        # if any not fleeing in a group or all fleeing in enemy group, all fleeing succeed
        # else, tests between fleeing and non fleeing. success flee,
        # failure - move to melee if any enemy targeted melee and succeed, else ranged

        # if any melee in a group or only ranged in other group, all ranged succeed
        # else, tests with enemy melees - if any failure, move to melee, on success ranged

        # if any enemy was moved to melee or selected melee, melees succeed, else keep ranged

        for moves, fleeing, melee, ranged, other_moves in [
            [moves1, fleeing1, new_melee1, new_ranged1, moves2],
            [moves2, fleeing2, new_melee2, new_ranged2, moves1]
        ]:
            self._moves_fleeing(moves, fleeing, melee, ranged, other_moves)

        for moves, ranged, melee, other_moves in [
            [moves1, new_ranged1, new_melee1, moves2],
            [moves2, new_ranged2, new_melee2, moves1]
        ]:
            self._moves_ranged(moves, ranged, melee, other_moves)

        for moves, melee, ranged, other_moves, other_melee in [
            [moves1, new_melee1, new_ranged1, moves2, new_melee2],
            [moves2, new_melee2, new_ranged2, moves1, new_melee1]
        ]:
            self._moves_melee(moves, melee, ranged, other_moves, other_melee)

        return fleeing1, new_ranged1, new_melee1, new_melee2, new_ranged2, fleeing2

    def _moves_fleeing(self, moves: dict, fleeing: set, melee: set, ranged: set, other_moves: dict) -> None:
        moved = []

        if any(d is not MoveDestination.FLEE for d in moves.values())\
                or all(d is MoveDestination.FLEE for d in other_moves.values()):
            fleeing.update({f for f, d in moves.items() if d is MoveDestination.FLEE})
            moved.extend(fleeing)

        else:
            for f, d in moves.items():
                if d is MoveDestination.FLEE:
                    dest = MoveDestination.FLEE
                    for opposed_f, opposed_d in other_moves.items():
                        if opposed_d is not MoveDestination.FLEE:
                            if self.move_test.test(opposed_f, f):
                                dest = MoveDestination.MELEE if MoveDestination.MELEE in (dest, opposed_d)\
                                    else MoveDestination.RANGED

                    if dest is MoveDestination.FLEE:
                        fleeing.add(f)
                    elif dest is MoveDestination.MELEE:
                        melee.add(f)
                    else:
                        ranged.add(f)
                    moved.append(f)

        for m in moved:
            del moves[m]

    def _moves_ranged(self, moves: dict, ranged: set, melee: set, other_moves: dict) -> None:
        moved = []

        if any(d is MoveDestination.MELEE for d in moves.values())\
                or all(d is MoveDestination.RANGED for d in other_moves.values()):
            for f, d in moves.items():
                if d is MoveDestination.RANGED:
                    ranged.add(f)
                    moved.append(f)

        else:
            for f, d in moves.items():
                if d is MoveDestination.RANGED:
                    dest = MoveDestination.RANGED
                    for opposed_f, opposed_d in other_moves.items():
                        if opposed_d is MoveDestination.MELEE:
                            if self.move_test.test(opposed_f, f):
                                dest = MoveDestination.MELEE

                    if dest is MoveDestination.MELEE:
                        melee.add(f)
                    else:
                        ranged.add(f)
                    moved.append(f)

        for m in moved:
            del moves[m]

    def _moves_melee(self, moves: dict, melee: set, ranged: set, other_moves: dict, other_melee: set) -> None:
        if other_moves or other_melee:
            melee.update(moves)
        else:
            ranged.update(moves)

    def _check_defeats(self, group: Iterable['Fighter']) -> Tuple[Iterable['Fighter'], Iterable['Fighter']]:
        return {f for f in group if f.resources[self.health].value > 0},\
            {f for f in group if f.resources[self.health].value == 0}
