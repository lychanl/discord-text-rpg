from dtrpg.core.game_object import GameObjectFactory
from dtrpg.core.events.event_result import (
    EventResult, ResourceChangeEventResult, ItemReceivedEventResult,
    InfoEventResult, RemoveItemEventResult
)
from dtrpg.core.item import ContainerOverflowException, InsufficientItemsException
from dtrpg.core.player import Player

from typing import Mapping


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


class InfoEvent(Event):
    def __init__(self):
        super().__init__(InfoEventResult)

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> InfoEventResult:
        event = self.create()
        event.player = player
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
            changes[player.resources[change.id]] = diff
        event.resource_changes = changes

        return event


class ItemReceiveEvent(Event):
    def __init__(self):
        super().__init__(ItemReceivedEventResult)
        self.item_factory = None

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> ItemReceivedEventResult:
        event = self.create()
        stack = params['item_factory'].create()

        event.item = stack.item
        event.number = stack.stack

        try:
            player.items.add(stack)
        except ContainerOverflowException as e:
            event.overflow = e

        return event


class RemoveItemEvent(Event):
    def __init__(self):
        super().__init__(RemoveItemEventResult)
        self.item = None
        self.number = 1

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> RemoveItemEventResult:
        event = self.create()

        number = params['number']
        item = params['item']

        event.item = item
        event.number = number

        try:
            player.items.remove(item, number)
        except InsufficientItemsException:
            event.failed = True

        return event
