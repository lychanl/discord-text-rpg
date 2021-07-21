from datetime import datetime
from dtrpg.core.game_object import GameObject, GameObjectFactory
from dtrpg.core.creature.statistic import CreatureStatistics
from dtrpg.core.creature.bonus import Bonus, ResourceBonus
from dtrpg.core.item import (
    Item, ItemSlot, ItemStack, NotEquippableException, ItemNotEquippedException, SlotNotEquippedException
)

from typing import Iterable, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from dtrpg.core.clock import Clock
    from dtrpg.core.fighting.fight_action import Attack
    from dtrpg.core.events import Event


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
        self._clock = None
        self.timed_bonuses = {}

    def on_event(self, event: 'Event'):
        pass

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

    def _bonuses(self):
        bonus = Bonus()
        for item in self.equipped_items:
            if item.bonus:
                bonus += item.bonus
        for timed_bonus in self.timed_bonuses:
            bonus += timed_bonus
        return bonus

    @property
    def bonuses(self) -> Bonus:
        self.update_timed()
        return self._bonuses()

    def _get_first_expired_bonus(self, now: datetime) -> Tuple[Bonus, datetime]:
        first = None
        first_time = None
        for bonus, time in self.timed_bonuses.items():
            if time <= now and (not first_time or first_time > time):
                first = bonus
                first_time = time

        return first, first_time

    def _update_timed_resources(self, to: datetime) -> None:
        bonus = self._bonuses()

        for resource, value in self.resources.items():
            value.update_timed(bonus.resource_bonuses.get(resource, ResourceBonus()), to)

    def update_timed(self) -> None:
        if not self._clock:
            return

        now = self._clock.now()

        expired, expired_time = self._get_first_expired_bonus(now)

        while expired:
            self._update_timed_resources(expired_time)
            del self.timed_bonuses[expired]
            expired, expired_time = self._get_first_expired_bonus(now)

        self._update_timed_resources(now)

    @property
    def clock(self) -> 'Clock':
        return self._clock

    @clock.setter
    def clock(self, clock: 'Clock') -> None:
        self._clock = clock
        self.update_timed()

    def add_timed_bonus(self, bonus: Bonus, time: float) -> None:
        self.update_timed()
        target_time = self._clock.now_plus(time)
        if bonus in self.timed_bonuses:
            self.timed_bonuses[bonus] = max(self.timed_bonuses[bonus], target_time)
        else:
            self.timed_bonuses[bonus] = target_time


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

        for res in creature.resources.values():
            res.creature = creature

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
