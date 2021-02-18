from dtrpg.core.creature.skill import OpposedSkillTest, Skill
from dtrpg.core.tester import Tester
from dtrpg.core.events import Event, EventResult
from dtrpg.core.fighting.engine import StatusFlag

from enum import Enum
import random

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.fighting.fight import FightStatus
    from dtrpg.core.creature.creature import Fighter


class FightAction:
    def apply(self, taker: 'Fighter', **kwargs: Mapping) -> EventResult:
        raise NotImplementedError

    def can_take(self, taker: 'Fighter', status: 'FightStatus') -> bool:
        raise NotImplementedError

    def get_kwargs(self, taker: 'Fighter', status: 'FightStatus', **kwargs: Mapping) -> dict:
        return {}


class TargetedAction(FightAction):
    def apply(self, taker: 'Fighter', target: 'Fighter', **kwargs: Mapping) -> EventResult:
        raise NotImplementedError

    def get_possible_targets(self, taker: 'Fighter', status: 'FightStatus') -> bool:
        possible = set()

        if self.allow_target_self(taker):
            possible.add(taker)
        if self.allow_target_ally(taker):
            possible.update(status.allies(taker).keys())

        if self.allow_target_enemy(taker):
            enemies = status.enemies(taker)
            if self.allow_melee_range(taker):
                possible.update(e for e, flags in enemies.items() if StatusFlag.MELEE in flags)
            if self.allow_ranged_range(taker) and any(StatusFlag.RANGED in e for e in enemies.values()):
                possible.update(e for e, flags in enemies.items() if StatusFlag.RANGED in flags)

        return possible

    def can_take(self, taker: 'Fighter', status: 'FightStatus') -> bool:
        return bool(self.get_possible_targets(taker, status))

    def get_kwargs(self, taker: 'Fighter', status: 'FightStatus', **kwargs: Mapping) -> dict:
        priority = kwargs.get('target_priority', None)

        possible_targets = self.get_possible_targets(taker, status)

        select_from = [t for t in possible_targets if priority in status[t]] or list(possible_targets)

        return {'target': random.choice(select_from)}

    def allow_melee_range(self, taker: 'Fighter') -> bool:
        raise NotImplementedError

    def allow_ranged_range(self, taker: 'Fighter') -> bool:
        raise NotImplementedError

    def allow_target_self(self, taker: 'Fighter') -> bool:
        raise NotImplementedError

    def allow_target_enemy(self, taker: 'Fighter') -> bool:
        raise NotImplementedError

    def allow_target_ally(self, taker: 'Fighter') -> bool:
        raise NotImplementedError


class AttackAction(TargetedAction):
    def apply(self, taker: 'Fighter', target: 'Fighter') -> EventResult:
        return taker.attack.fire(taker, target=target)

    def allow_melee_range(self, taker: 'Fighter') -> bool:
        return True

    def allow_ranged_range(self, taker: 'Fighter') -> bool:
        return not taker.attack.ranged

    def allow_target_self(self, taker: 'Fighter') -> bool:
        return False

    def allow_target_enemy(self, taker: 'Fighter') -> bool:
        return True

    def allow_target_ally(self, taker: 'Fighter') -> bool:
        return False


class AttackResult(EventResult):
    def __init__(self):
        super().__init__()
        self.attacker = None
        self.target = None
        self.hits = []
        self.results = []


class Attack(Event):
    def __init__(self):
        super().__init__(AttackResult)
        self.attacks_number = 1

        self.ranged = False
        self.hit_skill_modifier = 0
        self.evasion_skill_modifier = 0

        self.on_hit = None
        self.on_miss = None

        self.hit_test = OpposedSkillTest()

    @property
    def hit_skill(self) -> 'Skill':
        return self.hit_test.skill

    @hit_skill.setter
    def hit_skill(self, skill: 'Skill') -> None:
        self.hit_test.skill = skill

    @property
    def evasion_skill(self) -> 'Skill':
        return self.hit_test.skill_versus

    @evasion_skill.setter
    def evasion_skill(self, skill: 'Skill') -> None:
        self.hit_test.skill_versus = skill

    @property
    def tester(self) -> 'Tester':
        return self.hit_test.tester

    @tester.setter
    def tester(self, tester: 'Tester') -> None:
        self.hit_test.tester = tester

    def _fire(self, player: 'Fighter', target: 'Fighter', **params: Mapping[str, object]) -> AttackResult:
        res = self.create()
        res.target = target
        res.attacker = player

        for _ in range(self.attacks_number):
            success = self.hit_test.test(player, target, self.hit_skill_modifier, self.evasion_skill_modifier)
            res.hits.append(success)

            if success and self.on_hit:
                attack_res = self.on_hit.fire(player, target=target)
            elif not success and self.on_miss:
                attack_res = self.on_miss.fire(player, target=target)
            else:
                attack_res = None

            res.results.append(attack_res)

        return res


class DamageResult(EventResult):
    def __init__(self):
        super().__init__()
        self.damage_dealt = None


class Damage(Event):
    def __init__(self):
        super().__init__(DamageResult)
        self.damage_tests_number = 1
        self.damage_test_mod = None
        self.damage_per_hit = None

        self.damaged_resource = None

        self.tester = None

    def _fire(
            self, player: 'Fighter', target: 'Fighter',
            **params: Mapping[str, object]) -> AttackResult:
        total_damage = 0
        for _ in range(self.damage_tests_number):
            if self.tester.test(self.damage_test_mod, target.armor):
                total_damage += self.damage_per_hit

        target.resources[self.damaged_resource].value -= (total_damage)

        res = self.create()
        res.damage_dealt = total_damage

        return res


class EmptyActionResult(EventResult):
    pass


class EmptyAction(FightAction):
    def apply(self, taker: 'Fighter') -> EmptyActionResult:
        return EmptyActionResult()

    def can_take(self, taker: 'Fighter') -> bool:
        return True


class FightActions(FightAction, Enum):
    def __init__(self, action: FightAction):
        self.action = action
        super().__init__()

    def apply(self, taker: 'Fighter', **kwargs: Mapping) -> EventResult:
        return self.action.apply(taker, **kwargs)

    def can_take(self, taker: 'Fighter', status: 'FightStatus') -> bool:
        return self.action.can_take(taker, status)

    def get_kwargs(self, taker: 'Fighter', status: 'FightStatus', **kwargs: Mapping) -> dict:
        return self.action.get_kwargs(taker, status)

    ATTACK = AttackAction()
    EMPTY = EmptyAction()
