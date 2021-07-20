from datetime import datetime
from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.game_exception import GameException

from enum import Enum
from operator import add

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.bonus import ResourceBonus
    from dtrpg.core.creature.creature import Creature
    from dtrpg.core.creature.player import Player


class InsufficientResourceError(GameException):
    def __init__(self, resource: 'Resource', required: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.resource = resource
        self.required = required


class Resource(GameObject):
    def __init__(self):
        super().__init__()
        self.vital = False


class CreatureResource(GameObject):
    def __init__(self):
        super().__init__()
        self._value = 0
        self._max = None
        self._creature = None
        self.resource = None

        self._base_gen_rate = None
        self._last_time = None
        self._accumulated = 0

    @property
    def value(self) -> int:
        if self._creature:
            self._creature.update_timed()
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = max(min(value, self.max) if self._max else value, 0)
        if self._creature:
            self._creature.update_timed()

    @property
    def max(self) -> int:
        bonus = 0
        if self._creature and self.resource in self._creature.bonuses.resource_bonuses:
            bonus = self._creature.bonuses.resource_bonuses[self.resource].max_value
        return self._max + bonus

    @max.setter
    def max(self, m: int) -> None:
        self._max = m
        if m:
            self._value = min(self._value, m)
        if self._creature:
            self._creature.update_timed()

    @property
    def base_gen_rate(self) -> int:
        return self._base_gen_rate

    @base_gen_rate.setter
    def base_gen_rate(self, rate: float) -> None:
        if self._creature:
            self._creature.update_timed()
        self._base_gen_rate = rate
        if self._creature:
            self._creature.update_timed()

    @property
    def creature(self) -> 'Creature':
        return self._creature

    @creature.setter
    def creature(self, c: int) -> None:
        self._creature = c
        if self._creature:
            self._creature.update_timed()

    def _update(self, to: datetime, max_value: int, gen_rate: int) -> None:
        if self._value == max_value or not gen_rate:
            self._last_time = None
            self._accumulated = 0

        elif not self._last_time:
            self._last_time = to
            self._accumulated = 0

        else:
            dt = self._creature.clock.diff(to, self._last_time)
            self._last_time = to
            self._accumulated += dt * gen_rate
            inc, self._accumulated = divmod(self._accumulated, 1)
            inc = int(inc)
            self._value = min(max_value, self._value + inc) if max_value else self._value + inc

            if self._value == max_value:
                self._last_time = None
                self._accumulated = 0

    def update_timed(self, bonus: 'ResourceBonus', to: datetime) -> None:
        self._update(
            to,
            bonus.max_value + self._max if self._max else 0,
            bonus.regen_rate + self._base_gen_rate if self._base_gen_rate else 0
        )

    @property
    def state(self) -> dict:
        return {
            'value': self._value,
            'last_time': self._last_time,
            'accumulated': self._accumulated,
        }

    @state.setter
    def state(self, state) -> None:
        self._value = state['value']
        self._last_time = state['last_time']
        self._accumulated = state['accumulated']


class CreatureResourceFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(CreatureResource)
        self.resource = None
        self.initial = 0
        self.max = None

        self.base_gen_rate = None

    def create(self) -> Resource:
        resource = self._create()
        resource.value = self.initial
        resource.max = self.max
        resource.resource = self.resource

        resource.base_gen_rate = self.base_gen_rate

        return resource


def _set(value: int, change: int) -> int:
    return change


class ResourceChangeOp(GameObject, Enum):
    def __init__(self, op: Callable):
        super().__init__()
        self.op = op

    def __call__(self, value: int, change: int) -> int:
        return self.op(value, change)

    ADD = add,
    SET = _set,


class ResourceChange(GameObject):
    def __init__(self):
        super().__init__()
        self.resource = None
        self.value = None
        self.op = ResourceChangeOp.ADD

    def apply(self, player: 'Player') -> int:
        old = player.resources[self.resource].value
        player.resources[self.resource].value = self.op(player.resources[self.resource].value, self.value)
        return player.resources[self.resource].value - old

    def can_apply(self, player: 'Player') -> bool:
        return self.op(player.resources[self.resource].value, self.value) >= 0


class ResourceCost(ResourceChange):
    @property
    def cost(self) -> int:
        return -self.value

    @cost.setter
    def cost(self, cost: int) -> None:
        self.value = -cost

    def can_take(self, player: 'Player') -> bool:
        return self.can_apply(player)

    def apply(self, player: 'Player') -> None:
        if not self.can_take(player):
            raise InsufficientResourceError(player.resources[self.resource], self.cost)
        super().apply(player)

    def assert_can_take(self, player: 'Player') -> None:
        if not self.can_take(player):
            raise InsufficientResourceError(player.resources[self.resource], self.cost)
