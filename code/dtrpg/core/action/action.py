from dtrpg.core.action.event import EventFactory, Event

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Player


class Action(EventFactory):

    def take(self, player: 'Player', *args: Iterable[str]) -> Event:
        raise NotImplementedError
