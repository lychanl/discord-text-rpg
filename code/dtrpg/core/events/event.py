from dtrpg.core.game_object import GameObjectFactory
from dtrpg.core.game_exception import GameException
from dtrpg.core.events.event_result import (
    AddTimedBonusEventResult, EventResult, ResourceChangeEventResult,
    InfoEventResult, ExceptionEventResult
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
            result = type(self)._fire(cpy, player)
        except GameException as e:
            result = ExceptionEventResult(e)

        if result:
            result.player = player

        player.on_event(self)

        return result

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

        if player.killed:
            player.events.register(player.on_killed)

        return event


class SequenceEvent(ComplexEvent):
    def __init__(self):
        super().__init__(EventResult)
        self.events = []

    def _fire(self, player: 'Player') -> None:
        for i, event in enumerate(self.events):
            player.events.register(event, **self._get_subevent_params(str(i)))


class ConditionEvent(ComplexEvent):
    def __init__(self):
        super().__init__(EventResult)
        self.true = None
        self.false = None
        self.condition = None

    def _fire(self, player: 'Player') -> None:
        if self.condition.meets(player):
            if self.true:
                player.events.register(self.true, **self._get_subevent_params('true'))
        else:
            if self.false:
                player.events.register(self.false, **self._get_subevent_params('false'))


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


class AddTimedBonusEvent(Event):
    def __init__(self):
        super().__init__(AddTimedBonusEventResult)
        self.bonus = None
        self.time = None

    def _fire(self, player: 'Player') -> AddTimedBonusEventResult:
        result = self.create()

        player.add_timed_bonus(self.bonus, self.time)

        result.bonus = self.bonus
        result.time = self.time

        return result
