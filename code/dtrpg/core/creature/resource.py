from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.game_exception import GameException

from enum import Enum
from operator import add

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.clock import Clock
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

        self._base_gen_rate = None
        self._clock = None
        self._last_time = None
        self._accumulated = 0

    @property
    def value(self) -> int:
        self._update()
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = max(min(value, self._max) if self._max else value, 0)
        self._update()

    @property
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, m: int) -> None:
        self._max = m
        if m:
            self._value = min(self._value, m)
        self._update()

    @property
    def base_gen_rate(self) -> int:
        return self._base_gen_rate

    @base_gen_rate.setter
    def base_gen_rate(self, rate: float) -> None:
        self._update()
        self._base_gen_rate = rate

    @property
    def clock(self) -> 'Clock':
        return self._clock

    @clock.setter
    def clock(self, clock: 'Clock') -> None:
        self._clock = clock
        self._update()

    def _update(self) -> None:
        if self._value == self._max or not self._clock or not self._base_gen_rate:
            self._last_time = None
            self._accumulated = 0

        elif not self._last_time:
            self._last_time = self._clock.now()
            self._accumulated = 0

        else:
            self._last_time, dt = self._clock.now_with_diff(self._last_time)
            self._accumulated += dt * self._base_gen_rate
            inc, self._accumulated = divmod(self._accumulated, 1)
            inc = int(inc)
            self._value = min(self._max, self._value + inc) if self._max else self._value + inc

            if self._value == self._max:
                self._last_time = None
                self._accumulated = 0


class CreatureResourceFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(CreatureResource)
        self.resource = None
        self.initial = 0
        self.max = None

        self.base_gen_rate = None
        self.clock = None

    def create(self) -> Resource:
        resource = self._create()
        resource.value = self.initial
        resource.max = self.max
        resource.resource = self.resource

        resource.base_gen_rate = self.base_gen_rate
        resource.clock = self.clock

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
