from dtrpg.core.events.action import Action, ActionArgument
from dtrpg.core.events.event import Event
from dtrpg.core.events.event_result import EventResult
from dtrpg.core.item import Item, TradeOffer, OfferNotFoundException
from dtrpg.core.creature import Player


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

    def _fire(self, player: Player) -> TradeEventResult:
        offer = self._get_offer(self.item)

        result = self.create()

        result.value = self._make_trade(player, offer, self.number)

        result.resource = offer.resource
        result.number = self.number
        result.item = self.item

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
        self.item = None

    def _fire(self, player: Player) -> TradeEventResult:
        result = self.create()

        if self.item:
            result.offers = [self._get_offer(self.item)]
        else:
            result.offers = self.offers

        return result


class OffersInfoAction(Action):
    def __init__(self):
        super().__init__()
        self.event = OffersInfoEvent()
        self.args = {'item': ActionArgument(Item)}


class BuyAction(Action):
    def __init__(self):
        super().__init__()
        self.event = BuyEvent()
        self.args = {'item': ActionArgument(Item), 'number': ActionArgument(int)}


class SellAction(Action):
    def __init__(self):
        super().__init__()
        self.event = SellEvent()
        self.args = {'item': ActionArgument(Item), 'number': ActionArgument(int)}
