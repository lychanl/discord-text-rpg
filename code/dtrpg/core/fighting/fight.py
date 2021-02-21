from dtrpg.core.events import ComplexEvent, EventResult
from dtrpg.core.fighting.engine import FightResult

from typing import List, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Fighter, Player


class FightEventResult(EventResult):
    def __init__(self):
        super().__init__()

        self.group1 = []
        self.group2 = []
        self.result = None
        self.events = []

        self.next = None
        self.on_killed = None

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

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> FightEventResult:
        result = self.create()

        enemies = [f.create() for f in params['enemy_factories']]

        result.group1 = [player]
        result.group2 = enemies

        result.result, result.events, killed, fled = params['fight_engine'].fight([player], enemies)

        if result.result == FightResult.GROUP1:
            if params['victory']:
                result.next = params['victory'].fire(player, **self._get_subevent_params('victory', params))
        elif result.result == FightResult.GROUP2:
            if params['defeat']:
                result.next = params['defeat'].fire(player, **self._get_subevent_params('defeat', params))
        else:
            if params['draw']:
                result.next = params['draw'].fire(player, **self._get_subevent_params('draw', params))

        if player in killed and player.on_killed:
            result.on_killed = player.on_killed.fire(player)

        return result
