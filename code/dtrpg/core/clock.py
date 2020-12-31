from dtrpg.core.game_object import GameObject

from typing import Tuple
from datetime import datetime


class Clock(GameObject):
    def __init__(self):
        super().__init__()
        self.base = 3600

    def now(self) -> datetime:
        return datetime.now()

    def now_with_diff(self, prev: datetime) -> Tuple[datetime, float]:
        now = datetime.now()
        delta = now - prev

        hours = delta.total_seconds() / 3600

        return now, hours
