from dtrpg.core.events.event import Event, EventResult

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.ability import Ability, AbilityGroup
    from dtrpg.core.creature import Player


class AddAbilityEventResult(EventResult):
    def __init__(self):
        super().__init__()

        self.ability: 'Ability' = None
        self.group: 'AbilityGroup' = None


class AddAbilityEvent(Event):
    def __init__(self):
        super().__init__(AddAbilityEventResult)

        self.ability: 'Ability' = None
        self.group: 'AbilityGroup' = None

    def _fire(self, player: 'Player') -> EventResult:
        player.add_ability(self.ability, self.group)

        result = self.create()
        result.ability = self.ability
        result.group = self.group
        return result
