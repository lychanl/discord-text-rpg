from dtrpg.core.events.action import Action
from dtrpg.core.events.event import Event
from dtrpg.core.events.event_result import EventResult
from dtrpg.core.item import Item, TradeOffer, OfferNotFoundException
from dtrpg.core.player import Player


from typing import Mapping


class TradeEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.item = None
        self.resource = None
        self.value = None
        self.number = 1


class BuyEventResult(TradeEventResult):
    pass


class SellEventResult(TradeEventResult):
    pass


class OffersEvent(Event):
    def __init__(self, clss: type):
        super().__init__(clss)

        self.offers = []

    def _get_offer(self, item: Item) -> TradeOffer:
        for o in self.offers:
            if o.item is item:
                return o

        raise OfferNotFoundException


class TradeEvent(OffersEvent):
    def __init__(self, clss: type):
        super().__init__(clss)

        self.number = 1

    def _fire(self, player: Player, **params: Mapping[str, object]) -> TradeEventResult:
        item = params['item']
        number = params['number']
        offer = self._get_offer(item)

        result = self.create()

        result.value = self._make_trade(player, offer, number)

        result.resource = offer.resource
        result.number = number
        result.item = item

        return result

    def _make_trade(self, player: Player, offer: TradeOffer, number: int) -> None:
        raise NotImplementedError


class BuyEvent(TradeEvent):
    def __init__(self):
        super().__init__(BuyEventResult)

    def _make_trade(self, player: Player, offer: TradeOffer, number: int) -> None:
        offer.buy(player, number)
        return number * offer.buy_value


class SellEvent(TradeEvent):
    def __init__(self):
        super().__init__(SellEventResult)

    def _make_trade(self, player: Player, offer: TradeOffer, number: int) -> None:
        offer.sell(player, number)
        return number * offer.sell_value


class OffersInfoEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.offers = None


class OffersInfoEvent(OffersEvent):
    def __init__(self):
        super().__init__(OffersInfoEventResult)

    def _fire(self, player: Player, **params: Mapping[str, object]) -> TradeEventResult:
        result = self.create()

        if 'item' in params:
            result.offers = [self._get_offer(params['item'])]
        else:
            result.offers = self.offers

        return result


class OffersInfoAction(Action):
    def __init__(self):
        super().__init__()
        self.event = OffersInfoEvent()
        self.args = {'item': Item}


class BuyAction(Action):
    def __init__(self):
        super().__init__()
        self.event = BuyEvent()
        self.args = {'item': Item, 'number': int}


class SellAction(Action):
    def __init__(self):
        super().__init__()
        self.event = SellEvent()
        self.args = {'item': Item, 'number': int}
