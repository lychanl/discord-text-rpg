import unittest

import dtrpg.core.item as item
import dtrpg.core.creature as creature


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


class TestTrade(unittest.TestCase):
    def test_offer_buy(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()

        i.max_stack = 10
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 10
        o.resource = res
        o.buy_value = 3
        o.item = i

        o.buy(p, 2)

        self.assertEqual(p.resources[res].value, 4)
        self.assertEqual(p.items.count(i), 2)

    def test_offer_buy_not_enough_cap(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()

        i.max_stack = 1
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 1
        o.resource = res
        o.buy_value = 3
        o.item = i

        self.assertRaises(item.ContainerCapacityException, lambda: o.buy(p, 2))
        self.assertEqual(p.resources[res].value, 10)
        self.assertEqual(p.items.count(i), 0)

    def test_offer_buy_not_enough_resource(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()

        i.max_stack = 1
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 1
        o.resource = res
        o.buy_value = 3
        o.item = i

        self.assertRaises(creature.InsufficientResourceError, lambda: o.buy(p, 5))
        self.assertEqual(p.resources[res].value, 10)
        self.assertEqual(p.items.count(i), 0)

    def test_offer_buy_no_value(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()

        i.max_stack = 1
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 1
        o.resource = res
        o.item = i

        self.assertRaises(item.OfferNotFoundException, lambda: o.buy(p, 2))
        self.assertEqual(p.resources[res].value, 10)
        self.assertEqual(p.items.count(i), 0)

    def test_offer_sell(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()
        s = item.ItemStack()

        s.item = i
        s.stack = 4
        i.max_stack = 10
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 10
        p.items.add(s)
        o.resource = res
        o.sell_value = 3
        o.item = i

        o.sell(p, 2)

        self.assertEqual(p.resources[res].value, 16)
        self.assertEqual(p.items.count(i), 2)

    def test_offer_sell_not_enough_items(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()
        s = item.ItemStack()

        s.item = i
        s.stack = 4
        i.max_stack = 10
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 10
        p.items.add(s)
        o.resource = res
        o.sell_value = 3
        o.item = i

        self.assertRaises(item.InsufficientItemsException, lambda: o.sell(p, 5))

        self.assertEqual(p.resources[res].value, 10)
        self.assertEqual(p.items.count(i), 4)

    def test_offer_sell_no_value(self) -> None:
        p = creature.Player()
        o = item.TradeOffer()
        res = creature.Resource()
        r = creature.CreatureResource()
        i = item.Item()
        s = item.ItemStack()

        s.item = i
        s.stack = 4
        i.max_stack = 10
        r.value = 10
        r.resource = res
        p.resources = {res: r}
        p.items = item.Container()
        p.items.max_items = 10
        p.items.add(s)
        o.resource_id = res
        o.item = i

        self.assertRaises(item.OfferNotFoundException, lambda: o.sell(p, 2))

        self.assertEqual(p.resources[res].value, 10)
        self.assertEqual(p.items.count(i), 4)

    def test_items_requirement(self) -> None:
        req = item.ItemsRequirement()
        i = item.Item()
        c = creature.Creature()

        i.max_stack = 10
        c.items = item.Container()
        req.item = i
        req.number = 5

        self.assertFalse(req.meets(c))
        self.assertRaises(item.InsufficientItemsException, lambda: req.assert_meets(c))

        c.items.add(item.ItemStack(i, 3))

        self.assertFalse(req.meets(c))

        c.items.add(item.ItemStack(i, 3))
        self.assertTrue(req.meets(c))
        req.assert_meets(c)

    def test_item_equipped_requirement(self) -> None:
        pass
