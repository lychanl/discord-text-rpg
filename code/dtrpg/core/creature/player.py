from dtrpg.core.creature.creature import Fighter, FighterFactory
from dtrpg.core.creature.state_machine import InvalidStateException
from dtrpg.core.events import EventsManager, Event

from typing import Iterable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action
    from dtrpg.core.creature.state_machine import State, StateMachine


class Player(Fighter):
    def __init__(self):
        super().__init__()
        self.events = EventsManager(self)

        self.location = None
        self.base_actions = []
        self.default_attack = None
        self.base_armor = 0
        self.tactic = None
        self.available_tactics = ()
        self.variable_holder = None

        self.active_states = []

    @property
    def active_state(self) -> Tuple['State', 'StateMachine']:
        return self.active_states[-1] if self.active_states else (None, None)

    def enter_state_machine(self, state_machine: 'StateMachine') -> None:
        self.active_states.append((state_machine.initial, state_machine))

    def exit_state_machine(self, state_machine: 'StateMachine') -> None:
        if self.active_states and self.active_state[1] == state_machine:
            self.active_states.pop()
        else:
            raise InvalidStateException

    def on_event(self, event: 'Event') -> None:
        if self.active_states:
            self.active_state[0].on_event(self, event)

    def change_state(self, from_: 'State', to: 'State') -> None:
        if from_ is not self.active_state[0]:
            raise InvalidStateException
        self.active_states[-1] = (to, self.active_states[-1][1])

    @property
    def available_actions(self) -> Iterable['Action']:
        stateless_actions = self.base_actions + self.location.travel_actions + self.location.local_actions

        state, state_group = self.active_state

        if not state_group:
            return stateless_actions

        allowed = filter(
            lambda action: any(group in state_group.allowed_action_groups for group in action.groups),
            stateless_actions
        )

        return list(allowed) + state.actions


class PlayerFactory(FighterFactory):
    def __init__(self):
        super().__init__(Player)
        self.default_location = None
        self.base_actions = []
        self.default_attack = None
        self.available_tactics = ()
        self.default_variable_values = {}

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location
        player.base_actions = self.base_actions
        player.default_attack = self.default_attack
        player.available_tactics = self.available_tactics

        return player
