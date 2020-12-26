from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Resource


class Event(GameObject):
    pass


class EventFactory(GameObjectFactory):
    def __init__(self, event_type: type):
        super().__init__(event_type)


class ResourceChangeEvent(GameObject):
    def __init__(self):
        super().__init__()
        self._resource_changes = {}

    @property
    def resource_changes(self) -> Mapping['Resource', int]:
        return self._resource_changes

    @resource_changes.setter
    def resource_changes(self, changes: Mapping['Resource', int]) -> None:
        self._resource_changes = changes
