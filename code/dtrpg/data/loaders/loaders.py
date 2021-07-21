from typing import Tuple


class Loader:
    @property
    def can_load_str(self) -> bool:
        return False

    @property
    def try_load_obj_first(self) -> bool:
        return False

    def _split_typename_and_obj_name(self, typename: str) -> Tuple[str, str]:
        typename = typename.strip()

        if ' ' in typename:
            typename, obj_name = typename.split()
            typename = typename.strip()
            obj_name = obj_name.strip()
        else:
            obj_name = None

        return typename, obj_name

    def preload(self) -> object:
        raise NotImplementedError

    def load(
            self, obj: object, name: str, id: str, typename: str, objects_dict: dict,
            values: dict, game_objects: list, type_loaders: dict) -> object:
        raise NotImplementedError


class BuiltInLoader(Loader):
    def __init__(self, class_: type, try_load_obj_first: bool = False):
        super(BuiltInLoader, self).__init__()
        self._class = class_
        self._try_load_obj_first = try_load_obj_first

    @property
    def can_load_str(self) -> bool:
        return True

    @property
    def try_load_obj_first(self) -> bool:
        return self._try_load_obj_first

    @property
    def class_(self) -> type:
        return self._class

    def load(
            self, obj: object, name: str, id: str, typename: str, objects_dict: dict,
            values: dict, game_objects: list, type_loaders: dict) -> object:
        assert not typename, "Cannot explicitly specify type for this field"
        assert not name, "Cannot explicitly name this object"
        return self.class_(values)


class TypenameLoader(Loader):
    def __init__(self, types_dict: dict):
        super(TypenameLoader, self).__init__()
        self._types_dict = types_dict

    @property
    def can_load_str(self) -> bool:
        return True

    @property
    def class_(self) -> type:
        return type

    def load(
            self, obj: object, name: str, id: str, typename: str, objects_dict: dict,
            values: dict, game_objects: list, type_loaders: dict) -> object:
        assert not typename, "Cannot explicitly specify type for this field"
        assert not name, "Cannot explicitly name this object"
        return self._types_dict[values].class_
