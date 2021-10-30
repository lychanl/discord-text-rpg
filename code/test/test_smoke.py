from dtrpg.data.persistency.persistency import Persistency
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
        print('\n'.join(out))
        return ' '.join(' '.join(out).splitlines())


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

        clock = game.config.player_factory.clock
        action_points = [o for o in game.game_objects(core.creature.Resource) if o.id == 'action_points'][0]
        default_tester = game.game_objects(core.Tester)[0]

        clock.now = mock.Mock()
        clock.now.return_value.timestamp.return_value = 100
        clock.now_plus = mock.Mock()
        clock.now_plus.return_value.timestamp.return_value = 100
        clock.diff = mock.Mock()
        clock.diff.return_value = 0

        self.assertRegex(io.test('here'), r'.*not started.*start.*')
        self.assertRegex(io.test('start'), r'.*finally awake.*')
        self.assertRegex(io.test('invalid'), r'.*Invalid.*')
        self.assertRegex(io.test('mee'), r'.*Invalid.*Did you mean.*me.*')
        self.assertRegex(io.test('info item herb'), r'.*a herb.*')
        self.assertRegex(io.test('item linen jacket'), r'.*a linen jacket.*Armor \+1.*')
        self.assertRegex(io.test('me'), r'.*have 60/60 action points.*have 0 gold.*have 0/10 items.*in.*village.*')
        self.assertRegex(io.test('items'), r'.*Equipped.*Body: empty.*Inventory.*No items.*0/10.*')
        self.assertRegex(io.test('here'), r'.*You are in.*village.*Travel to coast.*')
        self.assertRegex(io.test('Travel to coast'), r'.*travel.*coast.*')
        self.assertRegex(io.test('here'), r'.*You are at.*coast.*Travel to village.*')
        self.assertRegex(io.test('fish'), r'.*You don\'t have fishing rod equipped.*')
        self.assertRegex(io.test('travel to village nothingthere'), r'.*travel.*village.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('get a job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('me'), r'.*have 58/60 action points.*have 10 gold.*have 0/10 items.*in.*village.*')

        clock.diff.return_value = 0.1

        self.assertRegex(io.test('me'), r'.*have 59/60 action points.*have 10.*You are in.*village.*')

        clock.diff.return_value = 0

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 0

        self.assertRegex(io.test('me'), r'.*have 0/60 action points.*')
        self.assertRegex(io.test('find a job'), r'.*don.*have.*action points.*1 needed.*')

        self.assertRegex(io.test('items'), r'.*No items.*0/10.*')
        self.assertRegex(io.test('drop fish'), r".*don't have enough items*")

        self.assertRegex(io.test('here'), r".*See offers.*Buy item.*Sell item.*")
        self.assertRegex(io.test('see offers'), r".*fish.*sell 6.*buy 15.*herbs.*sell 8.*fishing rod.*buy 25.*")

        game.player(TestIO.TEST_PLAYER).resources[action_points].value = 20

        # BUYING AND SELLING

        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('job'), r'.*job.*get.*5.*gold.*')
        self.assertRegex(io.test('buy fishing rod'), r".*buy 1x fishing rod.*25*")

        self.assertRegex(io.test('travel coast'), r'.*travel.*coast.*')
        self.assertRegex(io.test('equip fishing rod'), r'.*equip.*fishing rod.*')

        self.assertRegex(io.test('fish'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('fishing'), r'.*fish.* get 1x fish.*')
        self.assertRegex(io.test('items'), r'.*2x fish.*1/10.*')
        self.assertRegex(io.test('drop 2 fishes'), r'.*drop 2x fish*')

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

        # DIALOGUE

        self.assertRegex(io.test('Talk to the village elder'), r'.*approach the village elder.*Possible actions.*')
        self.assertRegex(io.test('me'), r'.*have 7/60 action points.*')
        self.assertRegex(io.test('travel to coast'), r'.*It would be rude to leave in the middle of a conversation.*')

        self.assertRegex(io.test('bye'), r'.*see you soon.*')

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
            io.test('hunt for forest rats'), r'.*Player fights against Forest Rat.*'
            + r'moves to melee.*'
            + r'Forest Rat attacks Player and hits, dealing 2 damage.*'
            + r'Player attacks Forest Rat and hits, dealing 1 damage.*'
            + r'Player was defeated!.*Forest Rat wins!.*'
            + r'You regain consciousness after some time.*'
            + r'You are tired and injured, but alive. You get 1 health points. You lose 8 action points.*')

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
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')

        self.assertRegex(io.test('item stones'), r'.*Attack: stone throw.*')
        self.assertRegex(io.test('stats'), r'.*Current attack: fist.*')
        self.assertRegex(io.test('equip stones'), r'.*equip stones.*hand.*')
        self.assertRegex(io.test('stats'), r'.*Current attack: stone throw.*')

        # OVERFLOW

        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*')
        self.assertRegex(io.test('gather stones'), r'.*get 1x stones.*dropped 1.*')

        # RESTART
        self.assertRegex(io.test('exit'), r'.*Are you sure.*')
        self.assertRegex(io.test('help'), r'.*Please confirm or cancel.*')
        self.assertRegex(io.test('no'), r'.*Ok!.*')
        self.assertRegex(io.test('yes'), r'.*Invalid.*')
        self.assertRegex(io.test('exit'), r'.*Are you sure.*')
        self.assertRegex(io.test('yes'), r'.*Bye.*')
        self.assertRegex(io.test('exit'), r'.*not started.*')
        self.assertRegex(io.test('start'), r'.*finally awake.*')
        self.assertRegex(io.test('me'), r'.*have 60/60 action points.*have 10/10 health.*')

        # QUESTS
        self.assertRegex(io.test('Journal'), 'No entries')
        self.assertRegex(io.test('Talk to the village elder'), 'How can I help')
        self.assertNotRegex(io.test('How can I help?'), 'What to do next')
        self.assertRegex(io.test('Bye'), 'see you soon')

        self.assertRegex(io.test('job'), 'some fishermen')
        self.assertRegex(io.test('Talk to the village elder'), 'What to do next?')
        self.assertRegex(io.test('What to do next?'), 'catch some fish.*get 20 gold')
        self.assertRegex(io.test('Bye'), 'see you soon')

        self.assertRegex(io.test('Buy fishing rod'), 'You buy 1x fishing rod')
        self.assertRegex(io.test('Travel to the coast'), 'You travel')
        self.assertRegex(io.test('fish'), 'don\'t have fishing rod')
        self.assertRegex(io.test('equip fishing rod'), 'fishing rod.*hand')
        self.assertRegex(io.test('fish'), 'get 1x fish')
        self.assertRegex(io.test('Travel to the village'), 'You travel')
        self.assertRegex(io.test('Talk to the village elder'), 'What to do next?')
        self.assertRegex(io.test('What to do next?'), 'Tom.*coast')
        self.assertRegex(io.test('Bye'), 'see you soon')

        self.assertRegex(io.test('Travel to the coast'), 'You travel')
        self.assertNotRegex(io.test('here'), 'small bay')
        self.assertRegex(io.test('Travel to the small bay'), 'Invalid command')
        self.assertRegex(io.test('Talk to the fisherman'), 'need some help')
        self.assertRegex(io.test('Do you need some help?'), 'Yea.*Ready')
        self.assertRegex(io.test('No'), 'need some help')
        self.assertRegex(io.test('Do you need some help?'), 'Yea.*Ready')
        self.assertRegex(io.test('Yes'), 'awake on the coast')
        self.assertRegex(io.test('here'), 'in the small bay')
        self.assertRegex(io.test('search'), 'rusty spear')
        self.assertNotRegex(io.test('search'), 'rusty spear')
        self.assertRegex(io.test('Travel to the coast'), 'You travel')
        self.assertRegex(io.test('here'), 'small bay')

        # CUSTOM TACTIC

        self.assertRegex(io.test(
            'set custom tactic\nIf all enemies have high health and I have low health then flee' +
            '\nElse go to melee\nIf any ally is melee then do nothing\nElse attack (target priority low health)'),
            r'.*Tactic set.*'
        )

        self.assertRegex(
            io.test('tactic'),
            r'.*if all enemies.*high health.*and.*low health then flee.*else.*melee.' +
            r'*any ally.*melee.*do nothing.*else.*attack.*target priority low health.*'
        )

        self.assertRegex(io.test(
            'set custom tactic\nIf all enemies have high health and I have low health then flee' +
            '\nElse go to melee\nIf any ally is melee then do nothng\nElse attack (target priority low health)'),
            r'.*Did you mean.*ally is melee.*do nothing.*ally is melee.*do nothng.*'
        )

        self.assertRegex(io.test(
            'set custom tactic\nIf all enemies have high health and I have low health then flee' +
            '\nElse go to melee\nIf any ally'),
            r'.*unfinished command.*'
        )

        # SAVING
        me = io.test('me')
        journal = io.test('journal')
        items = io.test('items')
        tactic = io.test('tactic')

        persistency = Persistency(game)
        data = persistency.serialize()

        game.players = {}

        persistency.deserialize(data)

        self.assertEqual(me, io.test('me'))
        self.assertEqual(journal, io.test('journal'))
        self.assertEqual(items, io.test('items'))
        self.assertEqual(tactic, io.test('tactic'))
