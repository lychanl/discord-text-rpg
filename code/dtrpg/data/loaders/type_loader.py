from dtrpg.data.loaders import Loader
from dtrpg.data.loaders.qualifier import QualifierError, Qualifiers, QualifierCheckFailed

from typing import Tuple, Union


class AbstractTypeException(Exception):
    pass


class AttributeRedefinitionError(Exception):
    pass


class TypeLoader(Loader):
    def __init__(self, typename):
        super(TypeLoader, self).__init__()
        self._class = None
        self._abstract = False
        self._base = None
        self._attributes = {}
        self._enum = False
        self._typename = typename

    @property
    def can_load_str(self) -> bool:
        return self._enum

    @property
    def class_(self) -> type:
        return self._class

    @class_.setter
    def class_(self, c: type) -> None:
        self._class = c

    @property
    def enum(self) -> bool:
        return self._enum

    @enum.setter
    def enum(self, e: bool) -> None:
        self._enum = e

    @property
    def abstract(self) -> bool:
        return self._abstract

    @abstract.setter
    def abstract(self, a: bool) -> None:
        self._abstract = a

    @property
    def base(self) -> 'TypeLoader':
        return self._base

    @base.setter
    def base(self, b: 'TypeLoader') -> None:
        self._base = b

    def add_attribute(self, name: str, loader: Loader, qualifiers: Qualifiers) -> None:
        if name in self._attributes:
            raise KeyError

        if qualifiers.collection_only:
            raise QualifierError('Invalid collection-only qualifiers')

        self._attributes[name] = loader, qualifiers

    def preload(self) -> object:
        if self._abstract:
            raise AbstractTypeException(f'Cannot instantiaze object of type {self._typename} - it is abstract')
        if self._enum:
            raise AbstractTypeException(f'Cannot instantiaze object of type {self._typename} - it is an enum')
        return self._class()

    def _split_name_and_type(self, name: str) -> Tuple[str, str]:
        if name.startswith('(') and ')' in name:
            tokens = name[1:].split(')')
            assert len(tokens) == 2, "Invalid type specification"
            typename, attr_name = tokens
            return (attr_name.strip(), *self._split_typename_and_obj_name(typename))

        return name, None, None

    def _load(
        self, id: str, objects_dict: dict, values: dict, attr_values: dict,
        variables: dict, game_objects: list, type_loaders: dict
    ) -> Tuple[dict, dict, dict]:
        unused = {}

        for name, value in values.items():
            name, typename, obj_name = self._split_name_and_type(name)

            if name in self._attributes:
                if isinstance(value, str) and value.startswith('variable(') and value.endswith(')'):
                    variables[name] = value[len('variable('):-1]
                else:
                    attr_values[name] = self._attributes[name][0].load(
                        None, obj_name, obj_name or f'{id}.{name}', typename,
                        objects_dict, value, game_objects, type_loaders
                    )
            else:
                unused[name] = value

        for name, (_, qualifiers) in self._attributes.items():
            try:
                if name in attr_values:
                    qualifiers.check([attr_values[name]])
                elif name in variables:
                    qualifiers.check([object()])
                else:
                    qualifiers.check([])
            except QualifierCheckFailed as e:
                raise QualifierCheckFailed(f'Qualifier check failed for {name}: {e}') from e

        if self._base:
            return self._base._load(id, objects_dict, unused, attr_values, variables, game_objects, type_loaders)
        else:
            return unused, attr_values, variables

    def _load_enum(self, value: str) -> object:
        return self._class[value]

    def _load_obj(
            self, id: str, obj: object, objects_dict: dict, values: Union[dict, str],
            game_objects: list, type_loaders: dict) -> object:
        if obj is None:
            obj = self.preload()

        unused, attr_values, variables = self._load(id, objects_dict, values, {}, {}, game_objects, type_loaders)

        if unused:
            raise KeyError(f'Undefined attributes: {list(unused.keys())}')

        for name, value in attr_values.items():
            setattr(obj, name, value)
        for name, value in variables.items():
            obj.add_variable_property(name, value)

        return obj

    def load(
            self, obj: object, name: str, id: str, typename: str, objects_dict: dict,
            values: Union[dict, str], game_objects: list, type_loaders: dict) -> object:
        if self._enum:
            obj = self._load_enum(values)
        else:
            obj = self._load_obj(id, obj, objects_dict, values, game_objects, type_loaders)

        game_objects.append((name, obj))

        obj.id = id

        return obj
