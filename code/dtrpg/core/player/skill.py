from dtrpg.core.game_object import GameObject, GameObjectFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player.player import Player


class Skill(GameObject):
    def __init__(self):
        super().__init__()

        self.progression = None
        self.experience_from_test = None

    def calculate_experience(self, level: int, difficulty: int, success: bool) -> int:
        return eval(
            self.experience_from_test,
            {'__builtins__': None, 'level': level, 'difficulty': difficulty, 'success': success}
        )

    def get_next_level_experience(self, level: int) -> int:
        return eval(self.progression, {'__builtins__': None, 'level': level})


class PlayerSkill(GameObject):
    def __init__(self):
        super().__init__()

        self.skill = None
        self.value = 1
        self._experience = 0

    def add_experience(self, value: int) -> None:
        self._experience += value
        while self.skill.get_next_level_experience(self.value) <= self._experience:
            self.value += 1


class PlayerSkillFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(PlayerSkill)

        self.skill = None
        self.initial = 1

    def create(self) -> PlayerSkill:
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

    def test(self, player: 'Player') -> bool:
        value = player.skills[self.skill].value
        success = self.tester.test(value, self.difficulty)

        exp = self.skill.calculate_experience(value, self.difficulty, success)
        player.skills[self.skill].add_experience(exp)

        return success
