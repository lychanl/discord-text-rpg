from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.clock import Clock
    from dtrpg.core.player.player import Player


class InsufficientResourceError(Exception):
    def __init__(self, resource: 'Resource', required: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.resource = resource
        self.required = required


class Resource(GameObject):
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
        self._value = min(value, self._max) if self._max else value
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


class ResourceFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Resource)
        self._id = None
        self._initial = 0
        self._max = None

        self._base_gen_rate = None
        self._clock = None

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        self._id = id

    @property
    def initial(self) -> int:
        return self._initial

    @initial.setter
    def initial(self, initial: int) -> None:
        self._initial = initial

    @property
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, m: int) -> None:
        self._max = m

    @property
    def base_gen_rate(self) -> int:
        return self._base_gen_rate

    @base_gen_rate.setter
    def base_gen_rate(self, rate: float) -> None:
        self._base_gen_rate = rate

    @property
    def clock(self) -> 'Clock':
        return self._clock

    @clock.setter
    def clock(self, clock: 'Clock') -> None:
        self._clock = clock

    def create(self) -> Resource:
        resource = self._create()
        resource.value = self._initial
        resource.max = self._max

        resource.base_gen_rate = self._base_gen_rate
        resource.clock = self._clock

        return resource


class ResourceChange(GameObject):
    def __init__(self):
        super().__init__()
        self._id = None
        self._value = None

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        self._id = id

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    def apply(self, player: 'Player') -> int:
        player.resources[self.id].value = player.resources[self.id].value + self._value
        return self._value


class ResourceCost(ResourceChange):
    @property
    def cost(self) -> int:
        return -self.value

    @cost.setter
    def cost(self, cost: int) -> None:
        self.value = -cost

    def can_take(self, player: 'Player') -> bool:
        return player.resources[self.id].value >= self.cost

    def apply(self, player: 'Player') -> None:
        if not self.can_take(player):
            raise InsufficientResourceError(player.resources[self.id], self.cost)
        super().apply(player)
