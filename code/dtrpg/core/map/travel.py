from dtrpg.core.events import Action, EventResult, Event

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.player import Player
    from dtrpg.core.map.location import Location


class TravelEventResult(EventResult):
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
        super().__init__()

        self._event = TravelEvent()

    @property
    def from_(self) -> 'Location':
        return self._event.from_

    @from_.setter
    def from_(self, from_: 'Location') -> None:
        self._event.from_ = from_

    @property
    def to(self) -> 'Location':
        return self._event._to

    @to.setter
    def to(self, to: 'Location') -> None:
        self._event.to = to


class TravelEvent(Event):
    def __init__(self):
        super().__init__(TravelEventResult)

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

    def _fire(self, player: 'Player', **params: Mapping[str, object]) -> TravelEventResult:
        event = self.create()

        event.to = params['to']
        event.from_ = params['from_']
        event.player = player

        player.location = params['to']

        return event
