import unittest

import dtrpg.core.map as map_


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
