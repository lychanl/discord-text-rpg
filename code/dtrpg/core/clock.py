from dtrpg.core.game_object import GameObject

from typing import Tuple
from datetime import datetime


class Clock(GameObject):
    def __init__(self):
        super().__init__()
        self._base = 3600

    @property
    def base(self) -> int:
        return self._base

    @base.setter
    def base(self, base: int) -> None:
        self._base = base

    def now(self) -> datetime:
        return datetime.now()

    def now_with_diff(self, prev: datetime) -> Tuple[datetime, float]:
        now = datetime.now()
        delta = now - prev

        hours = delta.total_seconds() / 3600

        return now, hours
