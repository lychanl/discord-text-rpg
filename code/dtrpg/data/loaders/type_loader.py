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
    def class_(self, c: type) -> None:
        self._class = c

    def add_attribute(self, name: str, loader: Loader, qualifiers: Qualifiers) -> None:
        if name in self._attributes:
            raise KeyError

        if qualifiers.collection_only:
            raise QualifierError('Invalid collection-only qualifiers')

        self._attributes[name] = loader, qualifiers

    def preload(self) -> object:
        return self._class()

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        if obj is None:
            obj = self._class()

        attribute_values = {}
        for name, value in values.items():
            attribute_values[name] = self._attributes[name][0].load(None, objects_dict, value)

        for name, (_, qualifiers) in self._attributes.items():
            if name in attribute_values:
                qualifiers.check([attribute_values[name]])
            else:
                qualifiers.check([])

        for name, value in attribute_values.items():
            setattr(obj, name, value)

        return obj
