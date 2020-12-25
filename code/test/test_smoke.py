import unittest

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

        self.assertRegex(io.test('here'), r'.*not started.*start.*')
        self.assertRegex(io.test('start'), r'.*Welcome.*')
        self.assertRegex(io.test('invalid'), r'.*Invalid.*')
        self.assertRegex(io.test('here'), r'.*You are in.*village.*Travel to coast.*')
        self.assertRegex(io.test('Travel to coast'), r'.*travel.*coast.*')
        self.assertRegex(io.test('here'), r'.*You are at.*coast.*Travel to village.*')
        self.assertRegex(io.test('travel village'), r'.*travel.*village.*')
