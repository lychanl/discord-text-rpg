from dtrpg.core.game_object import GameObject
from dtrpg.core.events import BuyAction, SellAction, OffersInfoAction
from dtrpg.core.item import TradeOffer

from typing import Sequence, Iterable, TYPE_CHECKING

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


class Market(Location):
    def __init__(self):
        super().__init__()
        self.buy_action = BuyAction()
        self.sell_action = SellAction()
        self.offers_action = OffersInfoAction()

        self._local_actions = []

    @property
    def local_actions(self) -> Sequence['TravelAction']:
        return [self.offers_action, self.buy_action, self.sell_action] + self._local_actions

    @local_actions.setter
    def local_actions(self, local_actions: Sequence['TravelAction']) -> None:
        self._local_actions = local_actions

    @property
    def offers(self) -> Iterable[TradeOffer]:
        return self.offers_action.offers

    @offers.setter
    def offers(self, offers: Iterable[TradeOffer]) -> None:
        self.offers_action.event.offers = offers
        self.sell_action.event.offers = offers
        self.buy_action.event.offers = offers
