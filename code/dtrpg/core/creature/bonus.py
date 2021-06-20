from dtrpg.core.game_object import GameObject


def _dict_sum(dict1, dict2):
    new = dict(dict1)
    for key, value in dict2.items():
        new[key] = new.get(key, 0) + value

    return new


class Bonus(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self.statistic_bonuses = {}
        self.resource_bonuses = {}

    def __add__(self, other: 'Bonus') -> 'Bonus':
        new = Bonus()
        new.statistic_bonuses = _dict_sum(self.statistic_bonuses, other.statistic_bonuses)
        new.resource_bonuses = _dict_sum(self.resource_bonuses, other.resource_bonuses)
        return new


class ResourceBonus(GameObject):
    def __init__(self, max_value=0, regen_rate=0) -> None:
        super().__init__()
        self.max_value = max_value
        self.regen_rate = regen_rate

    def __add__(self, other: 'ResourceBonus') -> 'ResourceBonus':
        new = ResourceBonus()
        new.max_value = self.max_value + other.max_value
        new.regen_rate = self.regen_rate + other.regen_rate
        return new
