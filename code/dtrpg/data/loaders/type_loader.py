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

    def _load(self, objects_dict: dict, values: dict, attr_values: dict) -> Tuple[dict, dict]:
        unused = {}

        for name, value in values.items():
            if name in self._attributes:
                attr_values[name] = self._attributes[name][0].load(None, objects_dict, value)
            else:
                unused[name] = value

        for name, (_, qualifiers) in self._attributes.items():
            try:
                if name in attr_values:
                    qualifiers.check([attr_values[name]])
                else:
                    qualifiers.check([])
            except QualifierCheckFailed as e:
                raise QualifierCheckFailed(f'Qualifier check failed for {name}: {e}') from e

        if self._base:
            return self._base._load(objects_dict, unused, attr_values)
        else:
            return unused, attr_values

    def _load_enum(self, value: str) -> object:
        return self._class[value]

    def _load_obj(self, obj: object, objects_dict: dict, values: Union[dict, str]) -> object:
        if obj is None:
            obj = self.preload()

        unused, attr_values = self._load(objects_dict, values, {})

        if unused:
            raise KeyError(f'Undefined attributes: {list(unused.keys())}')

        for name, value in attr_values.items():
            setattr(obj, name, value)

        return obj

    def load(self, obj: object, objects_dict: dict, values: Union[dict, str]) -> object:
        if self._enum:
            return self._load_enum(values)
        else:
            return self._load_obj(obj, objects_dict, values)
