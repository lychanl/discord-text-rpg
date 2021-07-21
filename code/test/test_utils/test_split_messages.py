import unittest

from dtrpg import utils


class TestSplitMessages(unittest.TestCase):
    def test_no_split(self):
        self.assertSequenceEqual(
            utils.split_messages(['MESSAGE\nMESSAGE1', 'MESSAGE2'], 30),
            ['MESSAGE\nMESSAGE1\nMESSAGE2']
        )

    def test_split(self):
        self.assertEqual(
            utils.split_messages(['MESSAGE\nMESSAGE1', 'MESSAGE2'], 20),
            ['MESSAGE\nMESSAGE1', 'MESSAGE2']
        )

    def test_split_inside(self):
        self.assertEqual(
            utils.split_messages(['MESSAGE\nMESSAGE1', 'MESSAGE2'], 10),
            ['MESSAGE', 'MESSAGE1', 'MESSAGE2']
        )
