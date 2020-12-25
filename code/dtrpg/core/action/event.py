from dtrpg.core.game_object import GameObject, GameObjectFactory


class Event(GameObject):
    pass


class EventFactory(GameObjectFactory):
    def __init__(self, event_type: type):
        super().__init__(event_type)
