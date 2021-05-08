from dtrpg.core.events.event import Event
from dtrpg.core.events.event_result import EventResult

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class StateMachineInitEventResult(EventResult):
    def __init__(self):
        super().__init__()

        self.machine = None


class StateMachineExitEventResult(EventResult):
    def __init__(self):
        super().__init__()

        self.machine = None


class StateMachineInitEvent(Event):
    def __init__(self):
        super().__init__(StateMachineInitEventResult)

        self.machine = None

        self.require = True

    def _fire(self, player: 'Player') -> StateMachineInitEventResult:
        result = self._create()

        player.enter_state_machine(self.machine)

        result.machine = self.machine

        return result


class StateMachineExitEvent(Event):
    def __init__(self):
        super().__init__(StateMachineExitEventResult)

        self.machine = None

    def _fire(self, player: 'Player') -> StateMachineExitEventResult:
        result = self._create()

        player.exit_state_machine(self.machine)

        result.machine = self.machine

        return result
