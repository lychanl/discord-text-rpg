class Loader:
    pass


class BuiltInLoader(Loader):
    def __init__(self, _type: type):
        super(BuiltInLoader, self).__init__()
        self._type = _type
