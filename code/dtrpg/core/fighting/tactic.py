from dtrpg.core.game_object import GameObject
from dtrpg.core.fighting.engine import FightStatus, StatusFlag, MoveDestination
from dtrpg.core.fighting.fight_action import FightAction, EmptyAction

from enum import Enum

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.creature import Fighter


class Tactic(GameObject):
    def __init__(self):
        super().__init__()
        self.move_predicates = []
        self.action_predicates = []

    def get_move(self, fighter: 'Fighter', fight_status: 'FightStatus') -> MoveDestination:
        for p in self.move_predicates:
            if p.check(fighter, fight_status):
                return p.result

        return MoveDestination.MELEE if StatusFlag.MELEE in fight_status[fighter] else MoveDestination.RANGED

    def get_action(self, fighter: 'Fighter', fight_status: 'FightStatus') -> 'FightAction':
        for p in self.action_predicates:
            if p.check(fighter, fight_status):
                return p.result, p.result.get_kwargs(fighter, fight_status, **p.params)

        return EmptyAction(), {}


class TacticQuantifier(GameObject, Enum):
    def __init__(self, quantifier: Callable, getter: Callable):
        self.quantifier = quantifier
        self.getter = getter

        GameObject.__init__(self)
        Enum.__init__(self)

    ANY_ENEMY = any, lambda f, s: s.enemies(f).values()
    ALL_ENEMIES = all, lambda f, s: s.enemies(f).values()
    ANY_ALLY = any, lambda f, s: s.allies(f).values()
    ALL_ALLIES = all, lambda f, s: s.allies(f).values()
    SELF = all, lambda f, s: [s[f]]


class TacticCondition(GameObject):
    def __init__(self):
        super().__init__()
        self.quantifier = None
        self.condition = None

    def check(self, fighter: 'Fighter', fight_status: 'FightStatus') -> bool:
        return self.quantifier.quantifier(
            self.condition in flag for flag in self.quantifier.getter(fighter, fight_status)
        )


class TacticPredicate(GameObject):
    def __init__(self):
        super().__init__()
        self.conditions = ()
        self.result = None
        self.target_priority = None

    def check(self, fighter: 'Fighter', fight_status: 'FightStatus') -> bool:
        if not self.result.can_take(fighter, fight_status):
            return False

        return not self.conditions or all(c.check(fighter, fight_status) for c in self.conditions)

    @property
    def params(self) -> dict:
        params = {}
        if self.target_priority:
            params['target_priority'] = self.target_priority

        return params


class MovePredicate(TacticPredicate):
    pass


class ActionPredicate(TacticPredicate):
    pass
