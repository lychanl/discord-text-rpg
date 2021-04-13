
from dtrpg.core.item.container import ContainerOverflowException
from dtrpg.core.item.item import InsufficientItemsException
from dtrpg.core.events import Event, EventResult

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Player


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
