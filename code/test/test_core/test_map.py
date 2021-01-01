import unittest

import dtrpg.core.map as map_
import dtrpg.core.item as item


class TestMap(unittest.TestCase):
    def test_travel_action_location_setting(self) -> None:
        loc1 = map_.Location()
        loc2 = map_.Location()

        travel_action = map_.TravelAction()
        travel_action.to = loc2

        loc1.travel_actions = [travel_action]

        self.assertIn(travel_action, loc1.travel_actions)
        self.assertIs(travel_action.from_, loc1)
        self.assertIs(travel_action.to, loc2)

    def test_market_offers(self) -> None:
        market = map_.Market()

        o1 = item.TradeOffer()
        o2 = item.TradeOffer()

        market.offers = [o1, o2]

        self.assertEqual([o1, o2], market.buy_action.event.offers)
        self.assertEqual([o1, o2], market.sell_action.event.offers)
        self.assertEqual([o1, o2], market.offers_action.event.offers)