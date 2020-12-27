from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Resource
    from dtrpg.core.item import Item, ContainerOverflowException


class Event(GameObject):
    pass


class EventFactory(GameObjectFactory):
    def __init__(self, event_type: type):
        super().__init__(event_type)


class ResourceChangeEvent(Event):
    def __init__(self):
        super().__init__()
        self._resource_changes = {}

    @property
    def resource_changes(self) -> Mapping['Resource', int]:
        return self._resource_changes

    @resource_changes.setter
    def resource_changes(self, changes: Mapping['Resource', int]) -> None:
        self._resource_changes = changes


class ItemReceivedEvent(Event):
    def __init__(self):
        super().__init__()
        self._item = None
        self._number = 0
        self._overflow = None

    @property
    def item(self) -> 'Item':
        return self._item

    @item.setter
    def item(self, item: 'Item') -> None:
        self._item = item

    @property
    def number(self) -> item:
        return self._number

    @number.setter
    def number(self, number: int) -> None:
        self._number = number

    @property
    def overflow(self) -> 'ContainerOverflowException':
        return self._overflow

    @overflow.setter
    def overflow(self, overflow: 'ContainerOverflowException') -> None:
        self._overflow = overflow
