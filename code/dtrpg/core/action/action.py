from dtrpg.core.action.event import (
    EventFactory, Event, ResourceChangeEvent, ItemReceivedEvent,
    InfoEvent, RemoveItemEvent
)
from dtrpg.core.player import Player, ResourceChange, ResourceCost, InsufficientResourceError
from dtrpg.core.item import ContainerOverflowException, ItemStackFactory, Item, InsufficientItemsException


from typing import Iterable


class Action(EventFactory):
    def __init__(self, event_type: type):
        super().__init__(event_type)
        self._args = []
        self._costs = []

    @property
    def costs(self) -> Iterable['ResourceCost']:
        return self._costs

    @costs.setter
    def costs(self, costs: Iterable['ResourceCost']) -> None:
        self._costs = costs

    @property
    def args(self) -> Iterable[type]:
        return self._args

    @args.setter
    def args(self, args: Iterable[type]) -> None:
        self._args = args

    def check_requirements(self, player: 'Player') -> bool:
        return all(cost.can_take(player) for cost in self._costs)

    def _take(self, player: 'Player') -> Event:
        for cost in self._costs:
            if not cost.can_take(player):
                raise InsufficientResourceError(player.resources[cost.id], cost.cost)
        for cost in self._costs:
            cost.apply(player)

        return self.create()

    def take(self, player: 'Player', *args: Iterable[object]) -> Event:
        raise NotImplementedError


class InfoAction(Action):
    def __init__(self):
        super().__init__(InfoEvent)

    def take(self, player: 'Player', *args: Iterable[object]) -> InfoEvent:
        event = self._take(player)
        event.player = player
        return event


class ResourceChangesAction(Action):
    def __init__(self):
        super().__init__(ResourceChangeEvent)
        self._resource_changes = []

    @property
    def resource_changes(self) -> Iterable['ResourceChange']:
        return self._resource_changes

    @resource_changes.setter
    def resource_changes(self, changes: Iterable['ResourceChange']) -> None:
        self._resource_changes = changes

    def take(self, player: 'Player', *args: Iterable[object]) -> ResourceChangeEvent:
        event = self._take(player)

        changes = {}
        for change in self._resource_changes:
            diff = change.apply(player)
            changes[player.resources[change.id]] = diff
        event.resource_changes = changes

        return event


class ItemReceiveAction(Action):
    def __init__(self):
        super().__init__(ItemReceivedEvent)
        self._item_factory = None

    @property
    def item_factory(self) -> 'ItemStackFactory':
        return self._item_factory

    @item_factory.setter
    def item_factory(self, item_factory: 'ItemStackFactory') -> None:
        self._item_factory = item_factory

    def take(self, player: 'Player', *args: Iterable[object]) -> ItemReceivedEvent:
        event = self._take(player)
        stack = self._item_factory.create()

        event.item = stack.item
        event.number = stack.stack

        try:
            player.items.add(stack)
        except ContainerOverflowException as e:
            event.overflow = e

        return event


class RemoveItemAction(Action):
    def __init__(self):
        super().__init__(RemoveItemEvent)
        self._item = None
        self._number = None

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

    def take(self, player: 'Player', *args: Iterable[object]) -> RemoveItemEvent:
        event = self._take(player)

        number = self._number or args[0] or 1
        item = self._item or args[1]

        event.item = item
        event.number = number

        try:
            player.items.remove(item, number)
        except InsufficientItemsException:
            event.failed = True

        return event
