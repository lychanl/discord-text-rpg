from dtrpg.core.game_object import GameObject
from dtrpg.core.events.event_result import EventResult, ExceptionEventResult

from typing import Sequence, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.creature import Player


class Action(GameObject):
    def __init__(self):
        super().__init__()
        self.args = {}
        self.costs = []
        self.event = None
        self.groups = []

    def check_requirements(self, player: 'Player') -> bool:
        return all(cost.can_take(player) for cost in self.costs)

    def take(self, player: 'Player', **args: Mapping[str, object]) -> Sequence[EventResult]:
        try:
            for cost in self.costs:
                cost.assert_can_take(player)
            for cost in self.costs:
                cost.apply(player)

            player.events.register(self.event, **args)
        except Exception as e:
            player.events.results.append(ExceptionEventResult(e))

        return player.events.fire_all()


class ActionGroup(GameObject):
    pass
