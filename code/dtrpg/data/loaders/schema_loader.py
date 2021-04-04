from dtrpg.data.loaders.qualifier import NumberQualifier, QualifierError, Qualifiers
from dtrpg.data.loaders import BuiltInLoader, TypenameLoader
from dtrpg.data.loaders.attribute_loader import (
    AttributeLoader,
    SimpleAttributeLoader,
    CollectionLoader,
    DictLoader
)
from dtrpg.data.loaders.type_loader import (
    AttributeRedefinitionError,
    TypeLoader,
)

import importlib
from collections.abc import Iterable
from typing import Dict, Collection


class SchemaError(Exception):
    pass


class SchemaLoader:
    def __init__(self):
        self._type_loaders = {}

    def parse_schema(self, schema: dict) -> Dict[str, TypeLoader]:
        self._type_loaders = self._get_default_type_loaders()

        for name in schema:
            if name in self._type_loaders:
                raise SchemaError(f'Type redefinition: {name}')
            self._type_loaders[name] = TypeLoader()

        for name, type_schema in schema.items():
            try:
                self._parse_type(type_schema, self._type_loaders[name])
            except SchemaError as e:
                raise SchemaError(f'Error while parsing type {name}: {e}') from e

        return self._type_loaders

    def _get_default_type_loaders(self) -> Dict[str, TypeLoader]:
        loaders = {
            'str': BuiltInLoader(str),
            'int': BuiltInLoader(int),
            'float': BuiltInLoader(float),
            'bool': BuiltInLoader(bool),
            'object': BuiltInLoader(object, try_load_obj_first=True)
        }
        loaders['type'] = TypenameLoader(loaders)

        return loaders

    def _parse_type(self, schema: dict, obj: TypeLoader) -> None:
        for name, value in schema.items():
            self._parse_element(name, value, obj)

    def _parse_element(self, name: str, value: str, obj: TypeLoader) -> None:
        try:
            if name.startswith('_'):
                self._parse_special_element(name, value, obj)
            else:
                tokens = name.split()
                obj.add_attribute(tokens[-1], self._parse_attribute(value), self._parse_qualifiers(tokens[:-1]))
        except SchemaError as e:
            raise SchemaError(f'Error while parsing element {name}: {e}') from e
        except QualifierError as e:
            raise SchemaError(f'Invalid qualifiers for element {name}: {e}') from e
        except AttributeRedefinitionError as e:
            raise SchemaError(f'Redefinition of element {name}') from e

    def _parse_special_element(self, name: str, value: str, obj: TypeLoader) -> None:
        if name == '_class':
            try:
                module = '.'.join(value.split('.')[:-1])
                type_name = value.split('.')[-1]
                class_ = getattr(importlib.import_module(module), type_name)
                obj.class_ = class_
            except (ImportError, AttributeError) as e:
                raise SchemaError(f'Invalid class {value}') from e
        elif name == '_abstract':
            obj.abstract = bool(value)
        elif name == '_base':
            obj.base = self._type_loaders[value]
        elif name == '_enum':
            obj.enum = bool(value)
        else:
            raise SchemaError('Invalid special element')

    def _parse_qualifiers(self, tokens: Collection[str]) -> Qualifiers:
        qualifiers_list = [self._parse_qualifier(q) for q in tokens]
        return Qualifiers(*qualifiers_list)

    def _parse_attribute(self, type_: str) -> AttributeLoader:
        if isinstance(type_, str):
            return self._parse_simple_attribute(type_)
        elif isinstance(type_, dict):
            return self._parse_dict_attribute(type_)
        elif isinstance(type_, Iterable):
            return self._parse_collection_attribute(type_)
        else:
            raise SchemaError('Invalid attribute type')

    def _parse_simple_attribute(self, attribute: str) -> SimpleAttributeLoader:
        try:
            return SimpleAttributeLoader(self._type_loaders[attribute])
        except KeyError as e:
            raise SchemaError(f'Invalid type {attribute}') from e

    def _parse_qualifier(self, qualifier: str) -> NumberQualifier:
        if qualifier == 'required':
            return NumberQualifier(1, None)
        elif qualifier == 'optional':
            return NumberQualifier(0, 1)
        elif qualifier.startswith('x') and qualifier[1:].isdigit():
            n = int(qualifier[1:])
            return NumberQualifier(n, n)

    def _parse_collection_attribute(self, attribute: Collection[str]) -> CollectionLoader:
        elements = [
            (self._parse_simple_attribute(a.split()[-1]), self._parse_qualifiers(a.split()[:-1]))
            for a in attribute
        ]

        return CollectionLoader(*elements)

    def _parse_dict_attribute(self, attribute: Dict[str, str]) -> DictLoader:
        if len(attribute) != 1:
            raise SchemaError('Dict attribute must have single key-value pair')

        key, value = next(iter(attribute.items()))

        return DictLoader(self._parse_simple_attribute(key), self._parse_simple_attribute(value))
