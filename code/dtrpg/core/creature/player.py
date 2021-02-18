from dtrpg.core.creature.creature import Fighter, FighterFactory

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action
    from dtrpg.core.fighting import Attack


class Player(Fighter):
    def __init__(self):
        super().__init__()
        self.location = None
        self.items = None
        self.base_actions = []
        self.default_attack = None
        self.base_armor = 0
        self.tactic = None

    @property
    def armor(self) -> int:
        return self.base_armor

    @property
    def attack(self) -> 'Attack':
        return self.default_attack

    @property
    def available_actions(self) -> Iterable['Action']:
        return self.base_actions + self.location.travel_actions + self.location.local_actions


class PlayerFactory(FighterFactory):
    def __init__(self):
        super().__init__(Player)
        self.default_location = None
        self.container_factory = None
        self.base_actions = []
        self.base_armor = 0
        self.default_attack = None

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location
        player.items = self.container_factory.create()

        player.base_actions = self.base_actions

        player.base_armor = self.base_armor
        player.default_attack = self.default_attack

        return player
