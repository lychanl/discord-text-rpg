from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.creature.statistic import CreatureStatistics
from dtrpg.core.item import (
    Item, ItemSlot, ItemStack, NotEquippableException, ItemNotEquippedException, SlotNotEquippedException
)

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.figthting.fight_action import Attack


class Creature(GameObject):
    def __init__(self):
        super().__init__()

        self.resources = {}
        self.skills = {}
        self._statistics = {}
        self.statistics = CreatureStatistics(self)
        self.items = None
        self.item_slots = {}
        self.loot_events = ()

    def equip(self, item: 'Item') -> None:
        if not item.slot:
            raise NotEquippableException(item)

        self.items.remove(item, 1)

        if self.item_slots[item.slot]:
            try:
                self.unequip_slot(item.slot)
            except Exception:
                self.items.add(ItemStack(item, 1))
                raise

        self.item_slots[item.slot] = item

    def unequip(self, item: 'Item') -> None:
        if not item.slot or self.item_slots[item.slot] != item:
            raise ItemNotEquippedException(item)

        self.unequip_slot(item.slot)

    def unequip_slot(self, slot: 'ItemSlot') -> None:
        if self.item_slots[slot] is None:
            raise SlotNotEquippedException(slot)

        self.items.add(ItemStack(self.item_slots[slot], 1))

        self.item_slots[slot] = None

    @property
    def equipped_items(self) -> Iterable['Item']:
        return [v for v in self.item_slots.values() if v]


class Fighter(Creature):
    def __init__(self):
        super().__init__()
        self.tactic = None
        self.on_killed = None
        self.default_attack = None

    @property
    def killed(self) -> bool:
        return any(r.vital and cr.value == 0 for r, cr in self.resources.items())

    @property
    def attack(self) -> 'Attack':
        for item in self.equipped_items:
            if item and item.attack:
                return item.attack
        return self.default_attack


class FighterFactory(GameObjectFactory):
    def __init__(self, class_: type):
        super().__init__(class_)
        self.resource_factories = ()
        self.skill_factories = ()
        self.statistic_factories = ()
        self.tactic = None
        self.on_killed = None
        self.item_slots = ()
        self.container_factory = None
        self.default_attack = None

    def _create(self) -> Fighter:
        creature = super()._create()

        creature.resources = {
            f.resource: f.create() for f in self.resource_factories
        }
        creature.skills = {
            f.skill: f.create() for f in self.skill_factories
        }
        creature.statistics.statistics = {
            f.statistic: f.create() for f in self.statistic_factories
        }

        creature.tactic = self.tactic
        creature.on_killed = self.on_killed

        creature.item_slots = {slot: None for slot in self.item_slots}
        creature.items = self.container_factory.create() if self.container_factory else None

        return creature
