
from dtrpg.core.item.container import ContainerOverflowException
from dtrpg.core.item.item import InsufficientItemsException
from dtrpg.core.events import Event, EventResult

from typing import Mapping, TYPE_CHECKING

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
