from dtrpg.core.events.event import ComplexEvent
from dtrpg.core.events.event_result import EventResult

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class SkillTestEvent(ComplexEvent):
    def __init__(self):
        super().__init__(None)
        self.test = None
        self.success = None
        self.failure = None

    def _fire(self, player: 'Player') -> EventResult:
        success = self.test.test(player)
        if success:
            player.events.register(self.success, **self._get_subevent_params('success'))
        else:
            player.events.register(self.failure, **self._get_subevent_params('failure'))
