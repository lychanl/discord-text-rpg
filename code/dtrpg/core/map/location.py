from dtrpg.core.game_object import GameObject

from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.map.travel import TravelAction


class Location(GameObject):
    def __init__(self):
        super().__init__()
        self._travel_actions = []
        self.local_actions = []

    @property
    def travel_actions(self) -> Sequence['TravelAction']:
        return self._travel_actions

    @travel_actions.setter
    def travel_actions(self, travel_actions: Sequence['TravelAction']) -> None:
        for travel_action in travel_actions:
            travel_action.event.from_ = self

        self._travel_actions = travel_actions
