from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.figthting.fight_action import Attack


class Creature(GameObject):
    def __init__(self):
        super().__init__()

        self.resources = {}
        self.skills = {}


class Fighter(Creature):
    def __init__(self):
        super().__init__()
        self.tactic = None

    @property
    def armor(self) -> int:
        raise NotImplementedError

    @property
    def attack(self) -> 'Attack':
        raise NotImplementedError


class FighterFactory(GameObjectFactory):
    def __init__(self, class_: type):
        super().__init__(class_)
        self.resource_factories = ()
        self.skill_factories = ()
        self.tactic = None

    def _create(self) -> Fighter:
        creature = super()._create()

        creature.resources = {
            f.resource: f.create() for f in self.resource_factories
        }
        creature.skills = {
            f.skill: f.create() for f in self.skill_factories
        }

        creature.tactic = self.tactic

        return creature
