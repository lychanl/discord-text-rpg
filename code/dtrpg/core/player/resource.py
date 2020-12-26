from dtrpg.core.game_object import GameObject, GameObjectFactory


class Resource(GameObject):
    def __init__(self):
        super().__init__()
        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value


class ResourceFactory(GameObjectFactory):
    def __init__(self):
        super().__init__(Resource)
        self._id = None
        self._initial = 0

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        self._id = id

    @property
    def initial(self) -> int:
        return self._initial

    @initial.setter
    def initial(self, initial: int) -> None:
        self._initial = initial

    def create(self) -> Resource:
        resource = self._create()
        resource.value = self._initial
        return resource
