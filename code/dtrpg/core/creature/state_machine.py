from dtrpg.core.game_object import GameObject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player
    from dtrpg.core.events import Event


class InvalidStateException:
    def __init__(self):
        super().__init__()


class State(GameObject):
    def __init__(self):
        super().__init__()

        self.transitions = {}

    def on_event(self, player: 'Player', event: 'Event'):
        if event in self.transitions:
            transition = self.transitions[event]
            if transition.to:
                player.change_state(self, transition.to)
            if transition.event:
                player.events.register(transition.event)


class StateTransition(GameObject):
    def __init__(self):
        super().__init__()

        self.event = None
        self.to = None


class ActiveState(State):
    def __init__(self):
        super().__init__()

        self.actions = []


class StateMachine(GameObject):
    def __init__(self):
        super().__init__()

        self.initial = None


class ActiveStateMachine(GameObject):
    def __init__(self):
        super().__init__()

        self.allowed_action_groups = []
