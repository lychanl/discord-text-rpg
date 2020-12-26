class Loader:
    def preload(self) -> object:
        raise NotImplementedError

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        raise NotImplementedError


class BuiltInLoader(Loader):
    def __init__(self, class_: type):
        super(BuiltInLoader, self).__init__()
        self.class_ = class_

    def class_(self) -> type:
        return self.class_

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        return self.class_(values)
