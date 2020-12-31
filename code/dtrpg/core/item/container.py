from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.item.item import Item, ItemStack, InsufficientItemsException

from typing import Iterable


class ContainerOverflowException(Exception):
    def __init__(self, stack: ItemStack):
        self.stack = stack


class Container(GameObject):
    def __init__(self):
        super().__init__()
        self.max_items = 1
        self._items = []

    def add(self, stack: ItemStack) -> None:
        for s in self._items:
            if s.item is stack.item and s.stack < s.item.max_stack:
                max_change = min(s.item.max_stack - s.stack, stack.stack)
                stack.stack -= max_change
                s.stack += max_change

        while len(self._items) < self.max_items and stack.stack > 0:
            if stack.stack <= stack.item.max_stack:
                self._items.append(stack)
                return
            else:
                self._items.append(stack.take(stack.item.max_stack))
        if stack.stack > 0:
            raise ContainerOverflowException(stack)

    def remove(self, item: Item, number: int) -> None:
        if self.count(item) < number:
            raise InsufficientItemsException(item, number)

        to_remove = []
        for s in reversed(self._items):
            if s.item is item:
                max_change = min(s.stack, number)
                s.stack -= max_change
                number -= max_change
                if s.stack == 0:
                    to_remove.append(s)

        for e in to_remove:
            self._items.remove(e)

    def count(self, item: Item) -> int:
        return sum(stack.stack for stack in self._items if stack.item is item)

    @property
    def items(self) -> Iterable[Item]:
        return self._items

    def __len__(self) -> int:
        return len(self._items)


class ContainerFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Container)
        self.max_items = 1

    def create(self) -> Container:
        c = self._create()
        c.max_items = self.max_items
        return c
