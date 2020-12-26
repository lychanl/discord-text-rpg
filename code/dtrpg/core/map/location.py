from dtrpg.core.game_object import GameObject

from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.action import Action
    from dtrpg.core.map.travel import TravelAction


class Location(GameObject):
    def __init__(self):
        super().__init__()
        self._travel_actions = []
        self._local_actions = []

    @property
    def travel_actions(self) -> Sequence['TravelAction']:
        return self._travel_actions

    @travel_actions.setter
    def travel_actions(self, travel_actions: Sequence['TravelAction']) -> None:
        for travel_action in travel_actions:
            travel_action._from = self

        self._travel_actions = travel_actions

    @property
    def local_actions(self) -> Sequence['Action']:
        return self._local_actions

    @local_actions.setter
    def local_actions(self, local_actions: Sequence['Action']) -> None:
        self._local_actions = local_actions
