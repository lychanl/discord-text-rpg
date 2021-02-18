from dtrpg.core.creature.creature import Fighter, FighterFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.fighting import Attack


class NPCFighter(Fighter):
    def __init__(self):
        super().__init__()
        self._armor = 0
        self._attack = None

    @property
    def armor(self) -> int:
        return self._armor

    @armor.setter
    def armor(self, armor: int) -> None:
        self._armor = armor

    @property
    def attack(self) -> 'Attack':
        return self._attack

    @attack.setter
    def attack(self, attack: 'Attack') -> None:
        self._attack = attack


class NPCFighterFactory(FighterFactory):
    def __init__(self):
        super().__init__(NPCFighter)
        self.armor = 0
        self.attack = None

    def create(self) -> NPCFighter:
        npc = self._create()

        npc.attack = self.attack
        npc.armor = self.armor

        return npc
