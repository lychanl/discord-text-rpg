from dtrpg.core.game_object import GameObject


class EventResult(GameObject):
    def __init__(self):
        super().__init__()
        self.player = None


class InfoEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.params = None


class ResourceChangeEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.resource_changes = {}


class VariableSetEventResult(EventResult):
    def __init__(self):
        super().__init__()
        self.variable = None
        self.value = None


class ExceptionEventResult(EventResult):
    def __init__(self, e: Exception):
        super().__init__()
        self.exception = e
