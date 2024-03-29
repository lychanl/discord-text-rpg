from dtrpg.core.events import Action, EventResult, Event

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core.creature import Player
    from dtrpg.core.map.location import Location


class TravelEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.to = None
        self.from_ = None
        self.player = None


class TravelAction(Action):
    def __init__(self):
        super().__init__()

        self.event = TravelEvent()

    @property
    def from_(self) -> 'Location':
        return self.event.from_

    @from_.setter
    def from_(self, from_: 'Location') -> None:
        self.event.from_ = from_

    @property
    def to(self) -> 'Location':
        return self.event.to

    @to.setter
    def to(self, to: 'Location') -> None:
        self.event.to = to


class TravelEvent(Event):
    def __init__(self):
        super().__init__(TravelEventResult)

        self.to = None
        self.from_ = None

    def _fire(self, player: 'Player') -> TravelEventResult:
        event = self.create()

        event.to = self.to
        event.from_ = self.from_
        event.player = player

        player.location = self.to

        return event
