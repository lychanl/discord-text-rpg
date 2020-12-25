import unittest

from dtrpg.data.locale import LocalizedObject, LocalizedObjectFactory


class TestLocale(unittest.TestCase):
    def test_get_object_string(self) -> None:
        class TestObject(LocalizedObject):
            pass

        obj = TestObject()

        obj.add_class_string('TEST', 'class string')
        obj.add_string('TEST', 'object string')

        self.assertEqual(obj.strings['TEST'], 'object string')

    def test_get_class_string(self) -> None:
        class TestObject(LocalizedObject):
            pass

        obj = TestObject()

        obj.add_class_string('TEST', 'class string')

        self.assertEqual(obj.strings['TEST'], 'class string')

    def test_get_not_found_string(self) -> None:
        class TestObject(LocalizedObject):
            pass

        obj = TestObject()

        self.assertEqual(obj.strings['TEST'], 'TEST')

    def test_format_string_context(self) -> None:
        class TestObject(LocalizedObject):
            pass

        obj = TestObject()
        ctx = {'a': 1}

        self.assertEqual(obj.strings['TEST {a}', ctx], 'TEST 1')

    def test_format_string_self(self) -> None:
        class TestObject(LocalizedObject):
            def __init__(self):
                self.a = 1
                super().__init__()

        obj = TestObject()

        self.assertEqual(obj.strings['TEST {self.a}'], 'TEST 1')

    def test_factory_get_object_string(self) -> None:
        class TestObject(LocalizedObject):
            pass

        class TestFactory(LocalizedObjectFactory):
            def __init__(self):
                super().__init__(TestObject)

        factory = TestFactory()

        factory.add_string('TEST', 'object string')

        obj = factory.create()

        self.assertEqual(obj.strings['TEST'], 'object string')
