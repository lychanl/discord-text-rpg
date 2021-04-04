from dtrpg.core.creature.creature import Fighter, FighterFactory

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action
    from dtrpg.core.fighting import Attack


class Player(Fighter):
    def __init__(self):
        super().__init__()
        self.location = None
        self.base_actions = []
        self.default_attack = None
        self.base_armor = 0
        self.tactic = None
        self.available_tactics = ()
        self.variable_holder = None

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
        self.base_actions = []
        self.default_attack = None
        self.available_tactics = ()
        self.default_variable_values = {}

    def create(self) -> Player:
        player = self._create()

        player.location = self.default_location
        player.base_actions = self.base_actions
        player.default_attack = self.default_attack
        player.available_tactics = self.available_tactics

        return player
