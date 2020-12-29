class Loader:
    def preload(self) -> object:
        raise NotImplementedError

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        raise NotImplementedError


class BuiltInLoader(Loader):
    def __init__(self, class_: type):
        super(BuiltInLoader, self).__init__()
        self._class = class_

    @property
    def class_(self) -> type:
        return self._class

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        return self.class_(values)


class TypenameLoader(Loader):
    def __init__(self, types_dict: dict):
        super(TypenameLoader, self).__init__()
        self._types_dict = types_dict

    @property
    def class_(self) -> type:
        return type

    def load(self, obj: object, objects_dict: dict, values: dict) -> type:
        return self._types_dict[values].class_
