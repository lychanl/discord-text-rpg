from dtrpg.core.game_object import GameObject, GameObjectFactory


class InsufficientItemsException(Exception):
    def __init__(self, item: 'Item', number: int):
        self.item = item
        self.number = number


class Item(GameObject):
    def __init__(self):
        super().__init__()
        self.max_stack = 1


class ItemStack(GameObject):
    def __init__(self):
        super().__init__()
        self.item = None
        self.stack = 1

    def take(self, n: int) -> 'ItemStack':
        if n > self.stack:
            raise InsufficientItemsException(self.item, n)

        ret = ItemStack()
        ret.stack = n
        ret.item = self.item
        self.stack -= n

        return ret


class ItemStackFactory(GameObjectFactory):
    def __init__(self, clss: type = ItemStack):
        super().__init__(clss)
        self.item = None
        self.stack = 1

    def create(self) -> ItemStack:
        stack = self._create()
        stack.item = self.item
        stack.stack = self.stack
        return stack
