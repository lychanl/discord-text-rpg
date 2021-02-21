from dtrpg.core.game_object import GameObject


class EventResult(GameObject):
    pass


class InfoEventResult(GameObject):
    def __init__(self):
        super().__init__()
        self.player = None


class ResourceChangeEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.resource_changes = {}


class SequenceEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.results = []
