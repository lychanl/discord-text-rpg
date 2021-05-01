from dtrpg.core.game_object import GameObjectFactory
from dtrpg.core.game_exception import GameException
from dtrpg.core.events.event_result import (
    EventResult, ResourceChangeEventResult, InfoEventResult, VariableSetEventResult, ExceptionEventResult
)

import copy
import random

from typing import Mapping, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class EventsManager:
    def __init__(self, player: 'Player') -> None:
        self.player = player
        self.events = []
        self.results = []
        self.next = 0

    def register(self, event: 'Event', **kwargs: Mapping[str, object]) -> None:
        self.events.insert(self.next, (event, kwargs))
        self.next += 1

    def fire_all(self) -> Sequence[EventResult]:
        while self.events:
            event, kwargs = self.events.pop(0)
            self.next = 0

            result = event.fire(self.player, **kwargs)

            if result:
                self.results.append(result)

        results = self.results
        self.results = []
        return results


class Event(GameObjectFactory):
    def fire(self, player: 'Player', **kwargs: Mapping[str, object]) -> EventResult:
        cpy = copy.copy(self)
        cpy.__dict__.update(kwargs)
        cpy.params = kwargs

        try:
            return type(self)._fire(cpy, player)
        except GameException as e:
            return ExceptionEventResult(e)

    def _fire(self, player: 'Player') -> EventResult:
        raise NotImplementedError


class ComplexEvent(Event):
    def _get_subevent_params(self, subevent_id: str) -> Mapping[str, object]:
        return {
            key[(len(subevent_id) + 1):]: value
            for key, value in self.params.items()
            if key.startswith(f'{subevent_id}.')
        }


class InfoEvent(Event):
    def __init__(self):
        super().__init__(InfoEventResult)

    def _fire(self, player: 'Player') -> InfoEventResult:
        event = self.create()
        event.player = player
        event.params = self.params
        return event


class ResourceChangesEvent(Event):
    def __init__(self):
        super().__init__(ResourceChangeEventResult)
        self.resource_changes = []

    def _fire(self, player: 'Player') -> ResourceChangeEventResult:
        event = self.create()

        changes = {}
        for change in self.resource_changes:
            diff = change.apply(player)
            changes[change.resource] = diff
        event.resource_changes = changes

        return event


class SequenceEvent(ComplexEvent):
    def __init__(self):
        super().__init__(EventResult)
        self.events = []

    def _fire(self, player: 'Player') -> None:
        for i, event in enumerate(self.events):
            player.events.register(event, **self._get_subevent_params(str(i)))


class VariableSetEvent(Event):
    def __init__(self):
        super().__init__(VariableSetEventResult)
        self.variable = None
        self.value = None

    def _fire(self, player: 'Player') -> VariableSetEventResult:
        event = self.create()

        event.variable = self.variable
        event.value = self.value

        player.set_variable(self.variable, self.value)

        return event


class ChanceEvent(ComplexEvent):
    def __init__(self):
        super().__init__(EventResult)
        self.randomizer = random.random
        self.chance = 0.5
        self.if_ = None
        self.else_ = None

    def _fire(self, player: 'Player') -> None:
        if self.randomizer() <= self.chance and self.if_:
            player.events.register(self.if_, **self._get_subevent_params('if'))
        elif self.else_:
            player.events.register(self.else_, **self._get_subevent_params('else'))
