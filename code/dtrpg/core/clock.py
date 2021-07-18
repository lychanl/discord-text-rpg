from dtrpg.core.game_object import GameObject

from datetime import datetime, timedelta


class Clock(GameObject):
    def __init__(self):
        super().__init__()
        self.base = 3600

    def now(self) -> datetime:
        return datetime.now()

    def diff(self, current: datetime, prev: datetime) -> float:
        delta = current - prev

        hours = delta.total_seconds() / self.base

        return hours

    def now_plus(self, time: float) -> datetime:
        return datetime.now() + timedelta(seconds=time * self.base)
