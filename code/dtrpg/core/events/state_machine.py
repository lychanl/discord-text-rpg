from dtrpg.core.creature.state_machine import InvalidStateException
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


class StateRequirement(Event):
    def __init__(self):
        self.state = None
        self.state_machine = None

    def meets(self, player: 'Player') -> bool:
        return player.passive_state(self.state_machine) is self.state \
            or player.active_state is (self.state_machine, self.state)

    def assert_meets(self, player: 'Player') -> None:
        if not self.meets(player):
            raise InvalidStateException
