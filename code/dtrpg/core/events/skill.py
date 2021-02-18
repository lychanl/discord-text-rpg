from dtrpg.core.events.event import ComplexEvent
from dtrpg.core.events.event_result import EventResult

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class SkillTestEvent(ComplexEvent):
    def __init__(self):
        super().__init__(None)
        self.test = None
        self.success = None
        self.failure = None

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> EventResult:
        success = self.test.test(player)
        if success:
            return self.success.fire(player, **self._get_subevent_params('success', params))
        else:
            return self.failure.fire(player, **self._get_subevent_params('failure', params))
