from dtrpg.core.game_object import GameObjectFactory
from dtrpg.core.events.event_result import (
    EventResult, ResourceChangeEventResult, ItemReceivedEventResult,
    InfoEventResult, RemoveItemEventResult
)
from dtrpg.core.item import ContainerOverflowException, ItemStackFactory, Item, InsufficientItemsException
from dtrpg.core.player import Player, ResourceChange

from typing import Mapping


class Event(GameObjectFactory):
    def fire(self, player: 'Player', **kwargs: Mapping[str, object]) -> EventResult:
        params = {
            p: getattr(self, p) for p in dir(type(self))
            if isinstance(getattr(type(self), p), property) and p not in dir(GameObjectFactory)
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
        self._resource_changes = []

    @property
    def resource_changes(self) -> Mapping[str, 'ResourceChange']:
        return self._resource_changes

    @resource_changes.setter
    def resource_changes(self, changes: Mapping[str, 'ResourceChange']) -> None:
        self._resource_changes = changes

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
        self._item_factory = None

    @property
    def item_factory(self) -> 'ItemStackFactory':
        return self._item_factory

    @item_factory.setter
    def item_factory(self, item_factory: 'ItemStackFactory') -> None:
        self._item_factory = item_factory

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
        self._item = None
        self._number = 1

    @property
    def item(self) -> 'Item':
        return self._item

    @item.setter
    def item(self, item: 'Item') -> None:
        self._item = item

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, number: int) -> None:
        self._number = number

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
