from dtrpg.core.game_exception import GameException
from dtrpg.core.game_object import GameObject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.events.action import Action


class AbilityAlreadyInGroupException(GameException):
    def __init__(self, ability: 'Ability', group: 'AbilityGroup') -> None:
        super().__init__()
        self.ability = ability
        self.group = group


class Ability(GameObject):
    def __init__(self):
        super().__init__()

        self.action: 'Action' = None
        self.in_world: bool = False
        self.in_fight: bool = False


class AbilityGroup(GameObject):
    pass
