from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action


class Player(GameObject):
    def __init__(self):
        super().__init__()
        self.location = None
        self.resources = {}
        self.items = None
        self.base_actions = []

    @property
    def available_actions(self) -> Iterable['Action']:
        return self.base_actions + self.location.travel_actions + self.location.local_actions


class PlayerFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Player)
        self.default_location = None
        self.resource_factories = ()
        self.container_factory = None
        self.base_actions = []

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location
        player.resources = {
            f.id: f.create() for f in self.resource_factories
        }
        player.items = self.container_factory.create()

        player.base_actions = self.base_actions

        return player
