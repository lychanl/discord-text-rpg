from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.creature.statistic import CreatureStatistics

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.figthting.fight_action import Attack


class Creature(GameObject):
    def __init__(self):
        super().__init__()

        self.resources = {}
        self.skills = {}
        self._statistics = {}
        self.statistics = CreatureStatistics(self)


class Fighter(Creature):
    def __init__(self):
        super().__init__()
        self.tactic = None
        self.on_killed = None

    @property
    def killed(self) -> bool:
        return any(r.vital and cr.value == 0 for r, cr in self.resources.items())

    @property
    def attack(self) -> 'Attack':
        raise NotImplementedError


class FighterFactory(GameObjectFactory):
    def __init__(self, class_: type):
        super().__init__(class_)
        self.resource_factories = ()
        self.skill_factories = ()
        self.statistic_factories = ()
        self.tactic = None
        self.on_killed = None

    def _create(self) -> Fighter:
        creature = super()._create()

        creature.resources = {
            f.resource: f.create() for f in self.resource_factories
        }
        creature.skills = {
            f.skill: f.create() for f in self.skill_factories
        }
        creature.statistics.statistics = {
            f.statistic: f.create() for f in self.statistic_factories
        }

        creature.tactic = self.tactic
        creature.on_killed = self.on_killed

        return creature
