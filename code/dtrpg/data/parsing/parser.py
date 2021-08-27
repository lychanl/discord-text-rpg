import re
from typing import Any, Iterable, Type
from dtrpg.data.locale.localized_object import LocalizedObject


class ArgumentError(Exception):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class Parser(LocalizedObject):
    def __call__(self, string: str) -> Any:
        raise NotImplementedError


class NameParser(Parser):
    def __init__(self, type: Type, objects: Iterable[LocalizedObject]):
        super().__init__()
        self.objects = [
            o for o in objects if isinstance(o, type) and ('NAME' in o.strings or 'REGEX_NAME' in o.strings)
        ]

    def __call__(self, string: str) -> Any:
        for o in self.objects:
            if o.strings['NAME'].lower() == string.lower():
                return o
            if re.fullmatch(o.strings['REGEX_NAME'], string, re.IGNORECASE):
                return o

        raise ArgumentError(string)


class BaseTypeParser(Parser):
    def __init__(self, type: Type):
        super().__init__()
        self.type = type

    def __call__(self, string: str) -> Any:
        try:
            return self.type(string)
        except ValueError:
            raise ArgumentError(string)
