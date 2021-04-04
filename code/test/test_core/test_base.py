import unittest

from dtrpg.core.game_object import GameObject, GameObjectFactory


class TestPlayer(unittest.TestCase):
    def test_game_object_variables(self) -> None:
        class test(GameObject):
            def __init__(self):
                super().__init__()
                self.prop = None

        t = test()
        t.add_variable_property('prop', 'PROP')
        t.set_variable('PROP', 2)

        self.assertEqual(t.prop, 2)

    def test_game_object_factory_variables(self) -> None:
        class test(GameObject):
            def __init__(self):
                super().__init__()
                self.prop = None

        class factory(GameObjectFactory):
            def __init__(self):
                super().__init__(test)

        f = factory()
        f.add_variable_property('prop', 'PROP')
        f.default_variables['PROP'] = 2

        self.assertEqual(f.create().prop, 2)
