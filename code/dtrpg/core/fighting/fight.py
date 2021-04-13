from dtrpg.core.events import ComplexEvent, EventResult
from dtrpg.core.fighting.engine import FightResult

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Fighter, Player


class FightEventResult(EventResult):
    def __init__(self):
        super().__init__()

        self.group1 = []
        self.group2 = []
        self.result = None
        self.events = []

    @property
    def winners(self) -> List['Fighter']:
        if self.result == FightResult.GROUP1:
            return self.group1
        elif self.result == FightResult.GROUP2:
            return self.group2
        else:
            return None

    @property
    def losers(self) -> List['Fighter']:
        if self.result == FightResult.GROUP1:
            return self.group2
        elif self.result == FightResult.GROUP2:
            return self.group1
        else:
            return None


class FightEvent(ComplexEvent):
    def __init__(self):
        super().__init__(FightEventResult)
        self.fight_engine = None
        self.enemy_factories = []
        self.victory = None
        self.defeat = None
        self.draw = None

    def _fire(self, player: 'Player') -> FightEventResult:
        result = self.create()

        enemies = [f.create() for f in self.enemy_factories]

        result.group1 = [player]
        result.group2 = enemies

        result.result, result.events, killed, fled = self.fight_engine.fight([player], enemies)

        if result.result == FightResult.GROUP1:
            for enemy in enemies:
                if enemy.killed:
                    for event in enemy.loot_events:
                        player.events.register(event)

            if self.victory:
                player.events.register(self.victory, **self._get_subevent_params('victory'))
        elif result.result == FightResult.GROUP2:
            if self.defeat:
                player.events.register(self.defeat, **self._get_subevent_params('defeat'))
        else:
            if self.draw:
                player.events.register(self.draw, **self._get_subevent_params('draw'))

        if player in killed and player.on_killed:
            player.events.register(player.on_killed)

        return result
