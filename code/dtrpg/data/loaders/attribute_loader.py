from dtrpg.data.loaders import Loader
from dtrpg.data.loaders.qualifier import Qualifiers

from typing import Collection, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.data.loaders.type_loader import TypeLoader


class AmbigousTypeError(Exception):
    pass


class AttributeLoader(Loader):
    pass


class SimpleAttributeLoader(AttributeLoader):
    def __init__(self, type_loader: 'TypeLoader'):
        super(SimpleAttributeLoader, self).__init__()
        self._type_loader = type_loader

    @property
    def type_loader(self) -> 'TypeLoader':
        return self._type_loader

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        if isinstance(values, str):
            obj = objects_dict[values]
            if not isinstance(obj, self._type_loader.class_):
                raise TypeError
            return obj
        else:
            return self._type_loader.load(None, objects_dict, values)


class CollectionLoader(AttributeLoader):
    def __init__(self, *attributes: Collection[Tuple[SimpleAttributeLoader, Qualifiers]]):
        super(CollectionLoader, self).__init__()
        self._attributes = {
            a[0].type_loader.class_: a
            for a in attributes
        }
        if len(self._attributes) != len(attributes):
            raise TypeError("Duplicate types in collection scheme")

    def load(self, obj: object, objects_dict: dict, values: dict) -> object:
        collection = []

        for value in values:
            if isinstance(value, str):
                obj = objects_dict[value]
                if not any(isinstance(obj, t) for t in self._attributes):
                    raise TypeError
            else:
                if len(self._attributes) > 0:
                    raise AmbigousTypeError
                loader = next(iter(self._attributes))[0]
                obj = loader.load(None, objects_dict, value)
            collection.append(obj)

        objs_by_type = {}
        for o in collection:
            if type(o) in objs_by_type:
                objs_by_type[type(o)].append(o)
            else:
                objs_by_type[type(o)] = [o]

        for type_, (_, qualifiers) in self._attributes.items():
            qualifiers.check(objs_by_type[type_])

        return collection
