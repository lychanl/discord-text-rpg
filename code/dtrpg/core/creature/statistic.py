from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.creature import Creature


class Statistic(GameObject):
    pass


class CreatureStatistic(GameObject):
    def __init__(self, statistic: Statistic, base: int):
        super().__init__()
        self.statistic = statistic
        self.base = base


class CreatureStatistics:
    def __init__(self, creature: 'Creature'):
        self.creature = creature
        self.statistics = {}

    def __getitem__(self, statistic: Statistic):
        return self.statistics[statistic].base + self.creature.bonuses.statistic_bonuses.get(statistic, 0)

    def items(self):
        for stat in self.statistics:
            yield stat, self[stat]


class StatisticFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(CreatureStatistic)
        self.base = 0

    def create(self) -> CreatureStatistic:
        stat = self._create(self.statistic, self.base)

        return stat
