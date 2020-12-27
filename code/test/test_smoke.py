import unittest
from unittest import mock

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

        game.player(TestIO.TEST_PLAYER).resources['action_points'].value = 0

        self.assertRegex(io.test('me'), r'.*have 0/60 action points.*')
        self.assertRegex(io.test('find a job'), r'.*don.*have.*action points.*1 needed.*')
