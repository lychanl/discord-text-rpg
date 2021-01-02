from dtrpg.core.game_object import GameObject
from dtrpg.core.events.event_result import EventResult
from dtrpg.core.player import Player, InsufficientResourceError


from typing import Iterable, Mapping


class Action(GameObject):
    def __init__(self):
        super().__init__()
        self.args = {}
        self.costs = []
        self.event = None

    def check_requirements(self, player: 'Player') -> bool:
        return all(cost.can_take(player) for cost in self.costs)

    def take(self, player: 'Player', **args: Mapping[str, object]) -> EventResult:
        for cost in self.costs:
            if not cost.can_take(player):
                raise InsufficientResourceError(player.resources[cost.resource], cost.cost)
        for cost in self.costs:
            cost.apply(player)

        return self.event.fire(player, **args)

    def _take(self, player: 'Player', *args: Iterable[object]) -> EventResult:
        return self.event.fire(player)
