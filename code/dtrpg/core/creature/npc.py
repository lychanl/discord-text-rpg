from dtrpg.core.creature.creature import Fighter, FighterFactory


class NPCFighter(Fighter):
    def __init__(self):
        super().__init__()


class NPCFighterFactory(FighterFactory):
    def __init__(self):
        super().__init__(NPCFighter)
        self.attack = None
        self.loot_events = ()

    def create(self) -> NPCFighter:
        npc = self._create()

        npc.default_attack = self.attack
        npc.loot_events = self.loot_events

        return npc
