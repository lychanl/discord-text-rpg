class Loader:
    def preload(self) -> object:
        raise NotImplementedError

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        raise NotImplementedError


class BuiltInLoader(Loader):
    def __init__(self, _type: type):
        super(BuiltInLoader, self).__init__()
        self._type = _type

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        return self._type(values)
