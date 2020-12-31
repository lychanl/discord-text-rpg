from dtrpg.core.game_object import GameObject
from dtrpg.core.events.event_result import EventResult
from dtrpg.core.events.event import Event
from dtrpg.core.player import Player, ResourceCost, InsufficientResourceError


from typing import Iterable, Mapping


class Action(GameObject):
    def __init__(self):
        super().__init__()
        self._args = {}
        self._costs = []
        self._event = None

    @property
    def costs(self) -> Iterable['ResourceCost']:
        return self._costs

    @costs.setter
    def costs(self, costs: Iterable['ResourceCost']) -> None:
        self._costs = costs

    @property
    def args(self) -> Mapping[str, type]:
        return self._args

    @args.setter
    def args(self, args: Mapping[str, type]) -> None:
        self._args = args

    def check_requirements(self, player: 'Player') -> bool:
        return all(cost.can_take(player) for cost in self._costs)

    @property
    def event(self) -> Event:
        return self._event

    @event.setter
    def event(self, event: Event) -> None:
        self._event = event

    def take(self, player: 'Player', **args: Mapping[str, object]) -> EventResult:
        for cost in self._costs:
            if not cost.can_take(player):
                raise InsufficientResourceError(player.resources[cost.id], cost.cost)
        for cost in self._costs:
            cost.apply(player)

        return self._event.fire(player, **args)

    def _take(self, player: 'Player', *args: Iterable[object]) -> EventResult:
        return self._event.fire(player)
