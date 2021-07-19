from dtrpg.data.locale import LocalizedObject, LocalizedObjectFactory


class GameObject(LocalizedObject):
    def __init__(self):
        super().__init__()

    def finalize(self) -> None:
        pass


class GameObjectFactory(LocalizedObjectFactory):
    pass
