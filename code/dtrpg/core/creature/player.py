from dtrpg.core.creature.ability import AbilityAlreadyInGroupException
from dtrpg.core.creature.creature import Fighter, FighterFactory
from dtrpg.core.creature.state_machine import InvalidStateException, StateMachineAlreadyEnteredException
from dtrpg.core.events import Action, EventsManager, Event

from typing import Dict, Iterable, List, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.ability import Ability, AbilityGroup
    from dtrpg.core.creature.state_machine import ActiveState, PassiveState, State, StateMachine, PassiveStateMachine
    from dtrpg.core.fighting import Attack, Tactic
    from dtrpg.core.map.location import Location


class Player(Fighter):
    def __init__(self):
        super().__init__()
        self.events = EventsManager(self)

        self.location: 'Location' = None
        self.base_actions: Sequence[Action] = []
        self.default_attack: 'Attack' = None
        self.base_armor: int = 0
        self.tactic: 'Tactic' = None
        self.available_tactics: Sequence['Tactic'] = ()

        self.default_invalid_action_event: Event = None

        self.active_states: List['ActiveState'] = []
        self.passive_states: Dict['PassiveStateMachine', 'PassiveState'] = {}

    @property
    def invalid_action_event(self) -> Event:
        if self.active_state[1] and self.active_state[1].invalid_action_event:
            return self.active_state[1].invalid_action_event
        return self.default_invalid_action_event

    @property
    def active_state(self) -> Tuple['State', 'StateMachine']:
        return self.active_states[-1] if self.active_states else (None, None)

    def passive_state(self, machine: 'StateMachine') -> 'State':
        return self.passive_states.get(machine, None)

    def enter_state_machine(self, state_machine: 'StateMachine') -> None:
        if state_machine.active:
            self.active_states.append((state_machine.initial, state_machine))
        else:
            if state_machine in self.passive_states:
                raise StateMachineAlreadyEnteredException(state_machine)
            self.passive_states[state_machine] = state_machine.initial

    def exit_state_machine(self, state_machine: 'StateMachine') -> None:
        if state_machine.active and self.active_states and self.active_state[1] == state_machine:
            self.active_states.pop()
        elif not state_machine.active and state_machine in self.passive_states:
            del self.passive_states[state_machine]
        else:
            raise InvalidStateException

    def on_event(self, event: 'Event') -> None:
        if self.active_states:
            self.active_state[0].on_event(self, event)

        for state in self.passive_states.values():
            state.on_event(self, event)

    def change_state(self, from_: 'State', to: 'State') -> None:
        if from_.machine.active and from_ is self.active_state[0] and from_.machine is self.active_state[1]:
            self.active_states[-1] = (to, from_.machine)
        elif not from_.machine.active and from_ is self.passive_states.get(from_.machine, None):
            self.passive_states[from_.machine] = to
        else:
            raise InvalidStateException

    def add_ability(self, ability: 'Ability', group: 'AbilityGroup'):
        if group not in self.abilities:
            self.abilities[group] = []
        if ability in self.abilities[group]:
            raise AbilityAlreadyInGroupException(ability, group)

        self.abilities[group].append(ability)

    @property
    def available_actions(self) -> Iterable['Action']:
        actions = self.base_actions + self.location.travel_actions + self.location.local_actions + [
            ability.action for group in self.abilities.values() for ability in group if ability.in_world
        ]

        state, state_group = self.active_state

        if state_group:
            actions = list(filter(
                lambda action: any(group in state_group.allowed_action_groups for group in action.groups),
                actions
            )) + state.actions

        return list(filter(lambda a: a.visible(self), actions))


class PlayerFactory(FighterFactory):
    def __init__(self):
        super().__init__(Player)
        self.default_location: 'Location' = None
        self.base_actions: Sequence[Action] = []
        self.default_attack: 'Attack' = None
        self.available_tactics: Sequence['Tactic'] = ()
        # self.default_variable_values = {}
        self.default_invalid_action_event = None
        self.clock = None

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location
        player.base_actions = self.base_actions
        player.default_attack = self.default_attack
        player.available_tactics = self.available_tactics
        player.default_invalid_action_event = self.default_invalid_action_event
        player.clock = self.clock

        return player
