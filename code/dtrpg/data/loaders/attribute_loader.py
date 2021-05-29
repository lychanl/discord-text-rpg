from dtrpg.data.loaders import Loader
from dtrpg.data.loaders.qualifier import Qualifiers

from typing import Collection, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.data.loaders.type_loader import TypeLoader


class AmbigousTypeError(Exception):
    pass


class AttributeLoader(Loader):
    def _load_single(
        self, objects_dict: dict, values: dict, default_loader: 'TypeLoader', game_objects: list
    ) -> object:
        if default_loader and default_loader.try_load_obj_first and isinstance(values, str) and values in objects_dict:
            return objects_dict[values]
        if default_loader and default_loader.can_load_str or not isinstance(values, str):
            obj = default_loader.load(None, objects_dict, values, game_objects)
            if default_loader and not isinstance(obj, default_loader.class_):
                raise TypeError
            return obj
        elif isinstance(values, str):
            return objects_dict[values]
        raise AmbigousTypeError


class SimpleAttributeLoader(AttributeLoader):
    def __init__(self, type_loader: 'TypeLoader'):
        super(SimpleAttributeLoader, self).__init__()
        self._type_loader = type_loader

    @property
    def type_loader(self) -> 'TypeLoader':
        return self._type_loader

    def load(self, obj: object, objects_dict: dict, values: dict, game_objects: list) -> object:
        obj = self._load_single(objects_dict, values, self._type_loader, game_objects)
        if not isinstance(obj, self._type_loader.class_):
            raise TypeError(f'Invalid object type, {self._type_loader.class_.__name__} expected')
        return obj


class CollectionLoader(AttributeLoader):
    def __init__(self, *attributes: Collection[Tuple[SimpleAttributeLoader, Qualifiers]]):
        super(CollectionLoader, self).__init__()
        self._attributes = attributes

    def load(self, obj: object, objects_dict: dict, values: dict, game_objects: list) -> object:
        collection = []

        for value in values:
            default_loader = next(iter(self._attributes))[0].type_loader if len(self._attributes) == 1 else None
            obj = self._load_single(objects_dict, value, default_loader, game_objects)
            if not any(isinstance(obj, t[0].type_loader.class_) for t in self._attributes):
                raise TypeError
            collection.append(obj)

        objs_by_type = {}
        for o in collection:
            if type(o) in objs_by_type:
                objs_by_type[type(o)].append(o)
            else:
                objs_by_type[type(o)] = [o]

        for loader, qualifiers in self._attributes:
            qualifiers.check(objs_by_type.get(loader.type_loader.class_, []))

        return collection


class DictLoader(AttributeLoader):
    def __init__(self, types: Dict[(SimpleAttributeLoader, SimpleAttributeLoader)]):
        super(DictLoader, self).__init__()
        self._types = types

    def load(self, obj: object, objects_dict: dict, values: dict, game_objects: list) -> object:
        dict_ = {}

        key_loader = None
        value_loader = None

        if len(self._types) == 1:
            key_loader = next(iter(self._types.keys())).type_loader
            value_loader = next(iter(self._types.values())).type_loader

        for key, value in values.items():
            key_obj = self._load_single(objects_dict, key, key_loader, game_objects)
            val_obj = self._load_single(objects_dict, value, value_loader, game_objects)

            dict_[key_obj] = val_obj

        for key, value in dict_.items():
            if not any(
                isinstance(key, kt.type_loader.class_) and isinstance(value, vt.type_loader.class_)
                for kt, vt in self._types.items()
            ):
                raise TypeError(f"Key-value pair {type(key)}, {type(value)} does not match any specified")

        return dict_
