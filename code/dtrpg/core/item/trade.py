from dtrpg.core.game_object import GameObject
from dtrpg.core.item.item import InsufficientItemsException, ItemStack
from dtrpg.core.item.container import ContainerCapacityException
from dtrpg.core.player import Player, InsufficientResourceError


class OfferNotFoundException(Exception):
    pass


class TradeOffer(GameObject):
    def __init__(self):
        super().__init__()

        self.buy_value = None
        self.sell_value = None
        self.resource_id = None
        self.item = None

    def check_buy(self, player: Player, number: int) -> None:
        if not self.buy_value:
            raise OfferNotFoundException
        if player.resources[self.resource_id].value < number * self.buy_value:
            raise InsufficientResourceError(player.resources[self.resource_id], number * self.buy_value)
        if not player.items.can_add(self.item, number):
            raise ContainerCapacityException

    def check_sell(self, player: Player, number: int) -> None:
        if not self.sell_value:
            raise OfferNotFoundException
        if player.items.count(self.item) < number:
            raise InsufficientItemsException(self.item, number)

    def buy(self, player: Player, number: int) -> None:
        self.check_buy(player, number)

        player.resources[self.resource_id].value -= number * self.buy_value
        stack = ItemStack()
        stack.item = self.item
        stack.stack = number
        player.items.add(stack)

    def sell(self, player: Player, number: int) -> None:
        self.check_sell(player, number)

        player.resources[self.resource_id].value += number * self.sell_value
        player.items.remove(self.item, number)
