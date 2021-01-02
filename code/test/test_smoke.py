import unittest
from unittest import mock

from dtrpg import core
from dtrpg.io.text_io import TextIO
from main import prepare_game

import os


class TestIO(TextIO):
    TEST_PLAYER = 'Test'

    def test(self, command: str) -> str:
        print(f'> {command}')
        out = self.command(self.TEST_PLAYER, command)
        print(out)
        return ' '.join(out.splitlines())


GAME_ARGS = {
    'schema_path': os.path.join('..', 'worlds', 'schema.yaml'),
    'world_path': os.path.join('..', 'worlds', 'default'),
    'config_name': os.path.join('config'),
    'locale_path': os.path.join('..', 'worlds', 'default', 'locales', 'en'),
}


class TestSmoke(unittest.TestCase):
    def test_smoke(self) -> None:
        game = prepare_game(**GAME_ARGS)
        io = TestIO(game)

        clock = game.config.player_factory.resource_factories[0].clock
        action_points = io._get_object('action points', core.player.Resource)
        default_tester = game.game_objects(core.Tester)[0]

        clock.now = mock.Mock()
        clock.now.return_value = object()
        clock.now_with_diff = mock.Mock()
        clock.now_with_diff.return_value = (object(), 0)

        self.assertRegex(io.test('here'), r'.*not started.*start.*')
        self.assertRegex(io.test('start'), r'.*Welcome.*')
        self.assertRegex(io.test('invalid'), r'.*Invalid.*')
        self.assertRegex(io.test('me'), r'.*have 60/60 action points.*have 0 gold.*have 0/10 items.*in.*village.*')
        self.assertRegex(io.test('items'), r'.*No items.*0/10.*')
        self.assertRegex(io.test('here'), r'.*You are in.*village.*Travel to coast.*')
        self.assertRegex(io.test('Travel to coast'), r'.*travel.*coast.*')
        self.assertRegex(io.test('here'), r'.*You are at.*coast.*Travel to village.*')
        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fishing'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('items'), r'.*2x fish.*1/10.*')
        self.assertRegex(io.test('travel village'), r'.*travel.*village.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('get a job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('me'), r'.*have 56/60 action points.*have 10 gold.*have 1/10 items.*in.*village.*')

        clock.now_with_diff.return_value = object(), 0.1

        self.assertRegex(io.test('me'), r'.*have 57/60 action points.*have 10.*You are in.*village.*')

        clock.now_with_diff.return_value = object(), 0

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 0

        self.assertRegex(io.test('me'), r'.*have 0/60 action points.*')
        self.assertRegex(io.test('find a job'), r'.*don.*have.*action points.*1 needed.*')

        self.assertRegex(io.test('drop 2 fishes'), r'.*drop 2x fish*')
        self.assertRegex(io.test('items'), r'.*No items.*0/10.*')
        self.assertRegex(io.test('drop fish'), r".*don't have enough items*")

        self.assertRegex(io.test('here'), r".*See offers.*Buy item.*Sell item.*")
        self.assertRegex(io.test('see offers'), r".*fish.*sell 6.*buy 15.*herbs.*sell 8.*fishing rod.*buy 25.*")
        self.assertRegex(io.test('travel coast'), r'.*travel.*coast.*')

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 10

        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('travel village'), r'.*travel.*village.*')
        self.assertRegex(io.test('sell 2 fishes'), r'.*sell 2x fish for 12*')
        self.assertRegex(io.test('sell 2 fishes'), r".*don't have enough items*")
        self.assertRegex(io.test('buy rod'), r".*don't have enough gold*")
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('buy rod'), r".*buy 1x fishing rod.*25*")

        self.assertRegex(io.test('skills'), r".*Herbalism: 1.*")

        self.assertRegex(io.test('travel forest'), r'.*travel.*forest.*')

        default_tester.test = mock.Mock()
        default_tester.test.return_value = True

        self.assertRegex(io.test('herbs'), r'.*find some herbs.*get 1x herbs')
        self.assertRegex(io.test('search for herbs'), r'.*find some herbs.*get 1x herbs')
        self.assertRegex(io.test('skills'), r".*Herbalism: 1.*")

        default_tester.test.return_value = False

        self.assertRegex(io.test('herbs'), r'.*search.*but find nothing')
        self.assertRegex(io.test('herbs'), r'.*search.*but find nothing')
        self.assertRegex(io.test('skills'), r".*Herbalism: 2.*")
