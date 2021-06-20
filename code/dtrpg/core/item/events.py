
from dtrpg.core.events.event import ComplexEvent
from dtrpg.core.game_exception import GameException
from dtrpg.core.item.container import ContainerOverflowException
from dtrpg.core.item.item import (
    InsufficientItemsException, ItemNotEquippedException, FreeSpaceRequiredException, Item
)
from dtrpg.core.events import Event, EventResult, Requirement

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player


class ItemReceivedEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None
        self.number = 0
        self.overflow = None


class RemoveItemEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None
        self.number = 0
        self.failed = False


class ItemReceiveEvent(Event):
    def __init__(self):
        super().__init__(ItemReceivedEventResult)
        self.item_factory = None

    def _fire(self, player: 'Player') -> ItemReceivedEventResult:
        event = self.create()
        stack = self.item_factory.create()

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

    def _fire(self, player: 'Player') -> RemoveItemEventResult:
        event = self.create()

        event.item = self.item
        event.number = self.number

        try:
            player.items.remove(self.item, self.number)
        except InsufficientItemsException:
            event.failed = True

        return event


class EquipEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None


class EquipItemEvent(Event):
    def __init__(self):
        super().__init__(EquipEventResult)
        self.item = None

    def _fire(self, player: 'Player') -> EquipEventResult:
        event = self.create()

        player.equip(self.item)

        event.item = self.item
        return event


class UnequipEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None


class UnequipItemEvent(Event):
    def __init__(self):
        super().__init__(UnequipEventResult)
        self.item = None

    def _fire(self, player: 'Player') -> UnequipEventResult:
        event = self.create()

        player.unequip(self.item)

        event.item = self.item
        return event


class UnequipSlotEvent(Event):
    def __init__(self):
        super().__init__(UnequipEventResult)
        self.slot = None

    def _fire(self, player: 'Player') -> UnequipEventResult:
        event = self.create()

        item = player.item_slots[self.slot]

        player.unequip_slot(self.slot)

        event.item = item
        return event


class ItemsRequirement(Requirement):
    def __init__(self):
        super().__init__()
        self.item = None
        self.number = 1

    def meets(self, player: 'Player') -> bool:
        return player.items.count(self.item) > self.number

    def assert_meets(self, player: 'Player') -> None:
        if not self.meets(player):
            raise InsufficientItemsException(self.item, self.number)


class ItemEquippedRequirement(Requirement):
    def __init__(self):
        super().__init__()
        self.item = None

    def meets(self, player: 'Player') -> bool:
        return self.item in player.equipped_items

    def assert_meets(self, player: 'Player') -> None:
        if not self.meets(player):
            raise ItemNotEquippedException(self.item)


class FreeSpaceRequirement(Requirement):
    def __init__(self):
        super().__init__()
        self.slots = 1

    def meets(self, player: 'Player') -> bool:
        return player.items.max_items - len(player.items) >= self.slots

    def assert_meets(self, player: 'Player') -> None:
        if not self.meets(player):
            raise FreeSpaceRequiredException(self.slots)


class UnusableItemException(GameException):
    def __init__(self, item: Item) -> None:
        super().__init__()
        self.item = item


class UseItemEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None


class UseItemEvent(ComplexEvent):
    def __init__(self):
        super().__init__(UseItemEventResult)
        self.item = None

    def _fire(self, player: 'Player') -> UseItemEventResult:
        if not self.item.use:
            raise UnusableItemException(self.item)

        if not player.items.count(self.item):
            raise InsufficientItemsException(self.item, 1)

        if self.item.remove_on_use:
            player.items.remove(self.item, 1)

        player.events.register(self.item.use, **self._get_subevent_params('use'))

        result = self.create()
        result.item = self.item

        return result
