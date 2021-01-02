from random import random


class Tester:
    def test(self, value: int, difficulty: int) -> bool:
        raise NotImplementedError


class RandomTester(Tester):
    def test(self, value: int, difficulty: int) -> bool:
        prob = self._prob(value, difficulty)
        return random() <= prob

    def _prob(self, value: int, difficulty: int) -> float:
        raise NotImplementedError


class ProportionalTester(RandomTester):
    def _prob(self, value: int, difficulty: int) -> bool:
        if value == 0:
            return 0
        if difficulty == 0:
            return 1
        return 0.5 * (value / difficulty if value < difficulty else 2 - difficulty / value)


class DifferentialTester(RandomTester):
    def __init__(self):
        super().__init__()

        self.const = 20
        self.perc_limit = 5

    def _prob(self, value: int, difficulty: int) -> bool:
        base = 0.5 - (difficulty - value) / self.const
        return max(min(base, 1 - self.perc_limit / 100), self.perc_limit / 100)


class ThresholdTester(Tester):
    def test(self, value: int, difficulty: int) -> bool:
        return value >= difficulty
