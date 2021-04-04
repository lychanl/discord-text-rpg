from dtrpg.core.creature.creature import Fighter, FighterFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.fighting import Attack


class NPCFighter(Fighter):
    def __init__(self):
        super().__init__()
        self._armor = 0
        self._attack = None


class NPCFighterFactory(FighterFactory):
    def __init__(self):
        super().__init__(NPCFighter)
        self.armor = 0
        self.attack = None

    def create(self) -> NPCFighter:
        npc = self._create()

        npc.default_attack = self.attack

        return npc
