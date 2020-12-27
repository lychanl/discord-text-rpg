from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Iterable, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action
    from dtrpg.core.item import Container, ContainerFactory
    from dtrpg.core.map.location import Location
    from dtrpg.core.player.resource import Resource, ResourceFactory


class Player(GameObject):
    def __init__(self):
        super().__init__()
        self._location = None
        self._resources = {}
        self._items = None

    @property
    def location(self) -> 'Location':
        return self._location

    @location.setter
    def location(self, location: 'Location') -> None:
        self._location = location

    @property
    def available_actions(self) -> Iterable['Action']:
        return self._location.travel_actions + self._location.local_actions

    @property
    def resources(self) -> Mapping[str, 'Resource']:
        return self._resources

    @resources.setter
    def resources(self, resources: Mapping[str, 'Resource']) -> None:
        self._resources = resources

    @property
    def items(self) -> 'Container':
        return self._items

    @items.setter
    def items(self, items: 'Container') -> None:
        self._items = items


class PlayerFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Player)
        self._default_location = None
        self._resource_factories = ()
        self._container_factory = None

    @property
    def default_location(self) -> 'Location':
        return self._default_location

    @default_location.setter
    def default_location(self, location: 'Location') -> None:
        self._default_location = location

    @property
    def container_factory(self) -> 'ContainerFactory':
        return self._container_factory

    @container_factory.setter
    def container_factory(self, factory: 'ContainerFactory') -> None:
        self._container_factory = factory

    @property
    def resource_factories(self) -> Iterable['ResourceFactory']:
        return self._resource_factories

    @resource_factories.setter
    def resource_factories(self, rf: Iterable['ResourceFactory']) -> None:
        self._resource_factories = rf

    def create(self) -> Player:
        player = self._create()

        player.location = self._default_location
        player.resources = {
            f.id: f.create() for f in self._resource_factories
        }
        player.items = self._container_factory.create()

        return player
