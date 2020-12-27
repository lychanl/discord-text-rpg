import unittest

import dtrpg.core.item as item


class TestItem(unittest.TestCase):
    def test_item_stack_factory(self) -> None:
        i = item.Item()
        f = item.ItemStackFactory()
        f.item = i
        f.stack = 3
        s = f.create()

        self.assertEqual(s.stack, 3)
        self.assertIs(s.item, i)

    def test_container_factory(self) -> None:
        f = item.ContainerFactory()
        f.max_items = 3
        c = f.create()

        self.assertEqual(c.max_items, 3)

    def test_container_add(self) -> None:
        i1 = item.Item()
        i1.max_stack = 4
        i2 = item.Item()
        i2.max_stack = 1

        c = item.Container()
        c.max_items = 4

        f1 = item.ItemStackFactory()
        f1.stack = 3
        f1.item = i1
        f2 = item.ItemStackFactory()
        f2.item = i2

        c.add(f1.create())
        self.assertEqual(len(c), 1)
        self.assertEqual(c.count(i1), 3)

        c.add(f1.create())
        self.assertEqual(len(c), 2)
        self.assertEqual(c.count(i1), 6)

        c.add(f2.create())
        self.assertEqual(len(c), 3)
        self.assertEqual(c.count(i1), 6)
        self.assertEqual(c.count(i2), 1)

        c.add(f2.create())
        self.assertEqual(len(c), 4)
        self.assertEqual(c.count(i1), 6)
        self.assertEqual(c.count(i2), 2)

        with self.assertRaises(item.ContainerOverflowException):
            c.add(f2.create())
        self.assertEqual(len(c), 4)
        self.assertEqual(c.count(i1), 6)
        self.assertEqual(c.count(i2), 2)

        with self.assertRaises(item.ContainerOverflowException) as e:
            c.add(f1.create())
        self.assertEqual(len(c), 4)
        self.assertEqual(c.count(i1), 8)
        self.assertEqual(c.count(i2), 2)
        self.assertEqual(e.exception.stack.stack, 1)

    def test_container_remove(self) -> None:
        i1 = item.Item()
        i1.max_stack = 4
        i2 = item.Item()
        i2.max_stack = 1

        c = item.Container()
        c.max_items = 4

        f1 = item.ItemStackFactory()
        f1.stack = 4
        f1.item = i1
        f2 = item.ItemStackFactory()
        f2.item = i2

        c.add(f1.create())
        c.add(f1.create())
        c.add(f2.create())
        c.add(f1.create())

        with self.assertRaises(item.InsufficientItemsException):
            c.remove(i2, 2)
        self.assertEqual(c.count(i2), 1)
        self.assertEqual(len(c), 4)

        c.remove(i2, 1)
        self.assertEqual(c.count(i2), 0)
        self.assertEqual(len(c), 3)

        c.remove(i1, 2)
        self.assertEqual(c.count(i1), 10)
        self.assertEqual(len(c), 3)

        c.remove(i1, 6)
        self.assertEqual(c.count(i1), 4)
        self.assertEqual(len(c), 1)

    def test_container_add_more_than_max(self) -> None:
        i = item.Item()
        i.max_stack = 1
        s = item.ItemStack()
        s.item = i
        s.stack = 2

        c = item.Container()
        c.max_items = 4

        c.add(s)
        self.assertEqual(len(c), 2)
        self.assertEqual(c.count(i), 2)