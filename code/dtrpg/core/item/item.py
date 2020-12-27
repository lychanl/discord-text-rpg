from dtrpg.core.game_object import GameObject, GameObjectFactory


class InsufficientItemsException(Exception):
    def __init__(self, item: 'Item', number: int):
        self.item = item
        self.number = number


class Item(GameObject):
    def __init__(self):
        super().__init__()
        self._max_stack = 1

    @property
    def max_stack(self) -> int:
        return self._max_stack

    @max_stack.setter
    def max_stack(self, stack: int) -> None:
        self._max_stack = stack


class ItemStack(GameObject):
    def __init__(self):
        super().__init__()
        self._item = None
        self._stack = 1

    @property
    def stack(self) -> int:
        return self._stack

    @stack.setter
    def stack(self, stack: int) -> None:
        self._stack = stack

    @property
    def item(self) -> str:
        return self._item

    @item.setter
    def item(self, item: str) -> None:
        self._item = item

    def take(self, n: int) -> 'ItemStack':
        if n > self._stack:
            raise InsufficientItemsException(self._item, n)

        ret = ItemStack()
        ret.stack = n
        ret.item = self._item
        self._stack -= n

        return ret


class ItemStackFactory(GameObjectFactory):
    def __init__(self, clss: type = ItemStack):
        super().__init__(clss)
        self._item = None
        self._stack = 1

    @property
    def stack(self) -> int:
        return self._stack

    @stack.setter
    def stack(self, stack: int) -> None:
        self._stack = stack

    @property
    def item(self) -> str:
        return self._item

    @item.setter
    def item(self, item: str) -> None:
        self._item = item

    def create(self) -> ItemStack:
        stack = self._create()
        stack.item = self._item
        stack.stack = self._stack
        return stack
