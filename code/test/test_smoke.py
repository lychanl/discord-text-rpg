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
        action_points = io._get_object('action points', core.creature.Resource)
        default_tester = game.game_objects(core.Tester)[0]

        clock.now = mock.Mock()
        clock.now.return_value = object()
        clock.now_with_diff = mock.Mock()
        clock.now_with_diff.return_value = (object(), 0)

        self.assertRegex(io.test('here'), r'.*not started.*start.*')
        self.assertRegex(io.test('start'), r'.*Welcome.*')
        self.assertRegex(io.test('invalid'), r'.*Invalid.*')
        self.assertRegex(io.test('info item herb'), r'.*a herb.*')
        self.assertRegex(io.test('item linen jacket'), r'.*a linen jacket.*Armor \+1.*')
        self.assertRegex(io.test('me'), r'.*have 60/60 action points.*have 0 gold.*have 0/10 items.*in.*village.*')
        self.assertRegex(io.test('items'), r'.*Equipped.*Body: empty.*Inventory.*No items.*0/10.*')
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

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 20

        # BUYING AND SELLING

        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('travel village'), r'.*travel.*village.*')
        self.assertRegex(io.test('sell 2 fishes'), r'.*sell 2x fish for 12*')
        self.assertRegex(io.test('sell 2 fishes'), r".*don't have enough items*")
        self.assertRegex(io.test('buy linen jacket'), r".*don't have enough gold*")
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('buy linen jacket'), r".*buy 1x linen jacket.*30*")

        # EQUIPMENT

        self.assertRegex(io.test('stats'), r'.*Armor: 0.*')

        self.assertRegex(io.test('equip fish'), r'.*cannot be equipped.*')
        self.assertRegex(io.test('unequip from body'), r'.*anything equipped.*')

        self.assertRegex(io.test('equip linen jacket'), r'.*equip linen jacket.*body.*')
        self.assertRegex(io.test('items'), r'.*Body: linen jacket.*')
        self.assertRegex(io.test('stats'), r'.*Armor: 1.*')
        self.assertRegex(io.test('unequip linen jacket'), r'.*remove linen jacket.*body.*')
        self.assertRegex(io.test('stats'), r'.*Armor: 0.*')
        self.assertRegex(io.test('items'), r'.*Body: empty.*')

        self.assertRegex(io.test('equip linen jacket'), r'.*equip linen jacket.*body.*')
        self.assertRegex(io.test('items'), r'.*Body: linen jacket.*')
        self.assertRegex(io.test('unequip linen jacket'), r'.*remove linen jacket.*body.*')
        self.assertRegex(io.test('unequip linen jacket'), r'.*don\'t have linen jacket equipped.*')

        # SKILLS

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

        # FIGHT

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 10

        default_tester.test.return_value = True
        self.assertRegex(
            io.test('hunt rats'), r'.*Player fights against Forest Rat.*'
            + r'moves to melee.*'
            + r'Forest Rat attacks Player and hits, dealing 2 damage.*'
            + r'Player attacks Forest Rat and hits, dealing 1 damage.*'  # repeared 3 times
            + r'Forest Rat was defeated!.*Player wins!.*'
            + r'You get 1x small fur.*')

        self.assertRegex(io.test('me'), r'.*have 4/10 health.*')

        self.assertRegex(
            io.test('hunt rats'), r'.*Player fights against Forest Rat.*'
            + r'moves to melee.*'
            + r'Forest Rat attacks Player and hits, dealing 2 damage.*'
            + r'Player attacks Forest Rat and hits, dealing 1 damage.*'
            + r'Player was defeated!.*Forest Rat wins!.*'
            + r'You regain consciousness after some time.*'
            + r'You are tired and injured, but alive. You get 1 health points. You loose 8 action points.*')

        # TACTICS

        self.assertRegex(io.test('tactic'), r'.*Current tactic: melee.*move to melee.*attack if possible.*')
        self.assertRegex(io.test('tactic ranged'), r'.*move to ranged.*attack if possible.*')
        self.assertRegex(io.test('list tactics'), r'.*melee.*cautious melee.*ranged.*cautious ranged.*')
        self.assertRegex(io.test('set ranged tactic'), r'.*Tactic set.*')
        self.assertRegex(io.test('tactic'), r'.*Current tactic: ranged.*move to ranged.*attack if possible.*')

        # ATTACKS

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 10

        self.assertRegex(io.test('travel village'), r'.*travel.*village.*')
        self.assertRegex(io.test('travel coast'), r'.*travel.*coast.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')

        self.assertRegex(io.test('item stones'), r'.*Attack: stone throw.*')
        self.assertRegex(io.test('stats'), r'.*Current attack: fist.*')
        self.assertRegex(io.test('equip stones'), r'.*equip stones.*hand.*')
        self.assertRegex(io.test('stats'), r'.*Current attack: stone throw.*')
