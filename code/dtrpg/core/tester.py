from random import random


class Tester:
    def _test(self, value: int, difficulty: int) -> bool:
        raise NotImplementedError

    def test(self, value: int, difficulty: int) -> bool:
        if value == 0:
            return False
        if difficulty == 0:
            return True
        if difficulty == -1:
            return False
        return self._test(value, difficulty)


class RandomTester(Tester):
    def _test(self, value: int, difficulty: int) -> bool:
        prob = self._prob(value, difficulty)
        return random() <= prob

    def _prob(self, value: int, difficulty: int) -> float:
        raise NotImplementedError


class ProportionalTester(RandomTester):
    def _prob(self, value: int, difficulty: int) -> float:
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
    def _test(self, value: int, difficulty: int) -> bool:
        return value >= difficulty
