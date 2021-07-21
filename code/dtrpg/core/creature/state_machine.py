from dtrpg.core.game_object import GameObject
from dtrpg.core.game_exception import GameException

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player
    from dtrpg.core.events import Event


class InvalidStateException(GameException):
    def __init__(self):
        super().__init__()


class StateMachineAlreadyEnteredException:
    def __init__(self):
        super().__init__()


class State(GameObject):
    def __init__(self):
        super().__init__()

        self.transitions = {}
        self.machine = None

    def on_event(self, player: 'Player', event: 'Event'):
        if event in self.transitions:
            transition = self.transitions[event]
            if transition.to:
                player.change_state(self, transition.to)
            if transition.event:
                player.events.register(transition.event)


class ActiveState(State):
    def __init__(self):
        super().__init__()

        self.actions = []


class PassiveState(State):
    pass


class StateTransition(GameObject):
    def __init__(self):
        super().__init__()

        self.event = None
        self.to = None


class StateMachine(GameObject):
    def __init__(self, active: bool):
        super().__init__()

        self.initial = None
        self.active = active

    def finalize_set_state(self, state) -> None:
        if state.machine:
            raise ValueError('State is in two state machines')
        state.machine = self

    def finalize(self) -> None:
        self.finalize_set_state(self.initial)
        states = [self.initial]
        while states:
            state = states.pop()
            for tr in state.transitions.values():
                if tr.to and tr.to.machine is not self:
                    self.finalize_set_state(tr.to)
                    states.append(tr.to)


class PassiveStateMachine(StateMachine):
    def __init__(self):
        super().__init__(False)


class ActiveStateMachine(StateMachine):
    def __init__(self):
        super().__init__(True)

        self.invalid_action_event = None
        self.allowed_action_groups = []
