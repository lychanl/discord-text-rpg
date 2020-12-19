from dtrpg.data.loaders import Loader
from dtrpg.data.loaders.qualifier import QualifierError, Qualifiers


class AttributeRedefinitionError(Exception):
    pass


class TypeLoader(Loader):
    def __init__(self):
        super(TypeLoader, self).__init__()
        self._class = None
        self._attributes = {}

    @property
    def class_(self) -> type:
        return self._class

    @class_.setter
    def class_(self, c: type):
        self._class = c

    def add_attribute(self, name: str, loader: Loader, qualifiers: Qualifiers):
        if name in self._attributes:
            raise KeyError

        if qualifiers.collection_only:
            raise QualifierError('Invalid collection-only qualifiers')

        self._attributes[name] = loader, qualifiers
