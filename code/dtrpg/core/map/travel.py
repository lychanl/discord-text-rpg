from dtrpg.core.action import Event, EventFactory, Action

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Player
    from dtrpg.core.map.location import Location


class TravelEvent(Event):
    def __init__(self):
        super().__init__()
        self._to = None
        self._from = None
        self._player = None

    @property
    def from_(self) -> 'Location':
        return self._from

    @from_.setter
    def from_(self, from_: 'Location') -> None:
        self._from = from_

    @property
    def to(self) -> 'Location':
        return self._to

    @to.setter
    def to(self, to: 'Location') -> None:
        self._to = to

    @property
    def player(self) -> 'Player':
        return self._player

    @player.setter
    def player(self, player: 'Player') -> None:
        self._player = player


class TravelAction(Action):
    def __init__(self):
        super().__init__(TravelEvent)

        self._to = None
        self._from = None

    @property
    def from_(self) -> 'Location':
        return self._from

    @from_.setter
    def from_(self, from_: 'Location') -> None:
        self._form = from_

    @property
    def to(self) -> 'Location':
        return self._to

    @to.setter
    def to(self, to: 'Location') -> None:
        self._to = to

    def take(self, player: 'Player', *args: Iterable[str]) -> TravelEvent:
        event = self.create()

        event.to = self._to
        event.from_ = self._from
        event.player = player

        player.location = self.to

        return event
