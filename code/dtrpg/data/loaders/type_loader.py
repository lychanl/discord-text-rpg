from dtrpg.core.game_object import GameObject
from dtrpg.data.loaders import Loader
from dtrpg.data.loaders.qualifier import QualifierError, Qualifiers, QualifierCheckFailed

from typing import Tuple, Union


class AbstractTypeException(Exception):
    pass


class AttributeRedefinitionError(Exception):
    pass


class TypeLoader(Loader):
    def __init__(self):
        super(TypeLoader, self).__init__()
        self._class = None
        self._abstract = False
        self._base = None
        self._attributes = {}
        self._enum = False

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
        if self._abstract or self._enum:
            raise AbstractTypeException
        return self._class()

    def _load(
        self, objects_dict: dict, values: dict, attr_values: dict, variables: dict, game_objects: list
    ) -> Tuple[dict, dict, dict]:
        unused = {}

        for name, value in values.items():
            if name in self._attributes:
                if isinstance(value, str) and value.startswith('variable(') and value.endswith(')'):
                    variables[name] = value[len('variable('):-1]
                else:
                    attr_values[name] = self._attributes[name][0].load(None, objects_dict, value, game_objects)
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
            return self._base._load(objects_dict, unused, attr_values, variables, game_objects)
        else:
            return unused, attr_values, variables

    def _load_enum(self, value: str) -> object:
        return self._class[value]

    def _load_obj(self, obj: object, objects_dict: dict, values: Union[dict, str], game_objects: list) -> object:
        if obj is None:
            obj = self.preload()

        unused, attr_values, variables = self._load(objects_dict, values, {}, {}, game_objects)

        if unused:
            raise KeyError(f'Undefined attributes: {list(unused.keys())}')

        for name, value in attr_values.items():
            setattr(obj, name, value)
        for name, value in variables.items():
            obj.add_variable_property(name, value)

        return obj

    def load(self, obj: object, objects_dict: dict, values: Union[dict, str], game_objects: list) -> object:
        if self._enum:
            obj = self._load_enum(values)
        else:
            obj = self._load_obj(obj, objects_dict, values, game_objects)

        if issubclass(self.class_, GameObject):
            game_objects.append(obj)

        return obj
