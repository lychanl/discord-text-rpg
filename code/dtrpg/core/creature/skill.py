from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature.creature import Creature


class Skill(GameObject):
    def __init__(self):
        super().__init__()

        self.progression = None
        self.experience_from_test = None

    def calculate_experience(self, level: int, difficulty: int, success: bool) -> int:
        return eval(
            self.experience_from_test,
            {'__builtins__': None, 'level': level, 'difficulty': difficulty, 'success': success}
        ) if self.experience_from_test else 0

    def get_next_level_experience(self, level: int) -> int:
        return eval(self.progression, {'__builtins__': None, 'level': level})


class CreatureSkill(GameObject):
    def __init__(self):
        super().__init__()

        self.skill = None
        self.value = 1
        self.experience = 0

    def add_experience(self, value: int) -> None:
        if self.skill.progression:
            self.experience += value
            while self.skill.get_next_level_experience(self.value) <= self.experience:
                self.value += 1


class CreatureSkillFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(CreatureSkill)

        self.skill = None
        self.initial = 1

    def create(self) -> CreatureSkill:
        player_skill = self._create()
        player_skill.skill = self.skill
        player_skill.value = self.initial
        return player_skill


class SkillTest(GameObject):
    def __init__(self):
        super().__init__()

        self.skill = None
        self.difficulty = None
        self.tester = None

    def test(self, creature: 'Creature', modifier: int = 0) -> bool:
        value = creature.skills[self.skill].value + modifier
        success = self.tester.test(value, self.difficulty)

        exp = self.skill.calculate_experience(value, self.difficulty, success)
        creature.skills[self.skill].add_experience(exp)

        return success


class OpposedSkillTest(GameObject):
    def __init__(self):
        super().__init__()

        self.skill = None
        self.skill_versus = None
        self.tester = None

    def test(
            self, creature: 'Creature', creature_versus: 'Creature',
            modifier: int = 0, modifier_versus: int = 0) -> bool:
        value = creature.skills[self.skill].value + modifier
        versus = creature_versus.skills[self.skill_versus].value + modifier_versus
        success = self.tester.test(value, versus)

        exp = self.skill.calculate_experience(value, versus, success)
        exp_versus = self.skill_versus.calculate_experience(versus, value, not success)
        creature.skills[self.skill].add_experience(exp)
        creature_versus.skills[self.skill_versus].add_experience(exp_versus)

        return success
