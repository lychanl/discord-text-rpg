from dtrpg.core.game_object import GameObjectFactory
from dtrpg.core.events.event_result import EventResult, ResourceChangeEventResult, InfoEventResult, SequenceEventResult


from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class Event(GameObjectFactory):
    def fire(self, player: 'Player', **kwargs: Mapping[str, object]) -> EventResult:
        params = {
            p: getattr(self, p) for p in self.__dict__
            if p not in dir(GameObjectFactory)
        }

        params.update(kwargs)

        return self._fire(player, **params)

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> EventResult:
        raise NotImplementedError


class ComplexEvent(Event):
    def _get_subevent_params(self, subevent_id: str, params: Mapping[str, object]) -> Mapping[str, object]:
        return {
            key[(len(subevent_id) + 1):]: value for key, value in params.items() if key.startswith(f'{subevent_id}.')
        }


class InfoEvent(Event):
    def __init__(self):
        super().__init__(InfoEventResult)

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> InfoEventResult:
        event = self.create()
        event.player = player
        event.params = params
        return event


class ResourceChangesEvent(Event):
    def __init__(self):
        super().__init__(ResourceChangeEventResult)
        self.resource_changes = []

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> ResourceChangeEventResult:
        event = self.create()

        changes = {}
        for change in params['resource_changes']:
            diff = change.apply(player)
            changes[change.resource] = diff
        event.resource_changes = changes

        return event


class SequenceEvent(ComplexEvent):
    def __init__(self):
        super().__init__(SequenceEventResult)
        self.events = []

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> SequenceEventResult:
        event = self.create()

        event.results = [
            event.fire(player, **self._get_subevent_params(str(i), params))
            for i, event in enumerate(params['events'])
        ]

        return event
