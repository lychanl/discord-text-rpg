from typing import Mapping, Tuple, Union
from dtrpg.data.locale.formatter import LocaleFormatter


class DuplicateStringError(Exception):
    pass


class LocalizedObject:
    _class_strings = {}

    @property
    def strings(self) -> Mapping[str, str]:
        return self._strings_mapper

    @classmethod
    def add_class_string(cls, string: str, value: str) -> None:
        if string in cls._class_strings[cls]:
            raise DuplicateStringError
        cls._class_strings[cls][string] = value

    def add_string(self, string: str, value: str) -> None:
        if string in self._obj_strings:
            raise DuplicateStringError
        self._obj_strings[string] = value

    def __init__(self):
        if type(self) not in self._class_strings:
            self._class_strings[type(self)] = {}

        self._obj_strings = {}
        self._strings_mapper = ObjectStrings(self._obj_strings, self._class_strings[type(self)], self)


class ObjectStrings:
    formatter = LocaleFormatter()

    def __init__(self, obj_strings: Mapping[str, str], cls_strings: Mapping[str, str], obj: LocalizedObject):
        self._obj_strings = obj_strings
        self._cls_strings = cls_strings
        self._obj = obj

    def __getitem__(self, args: Union[str, Tuple[str, dict]]) -> str:
        if isinstance(args, str):
            string = args
            ctx = {}
        else:
            string, ctx = args
            ctx = dict(ctx)

        ctx.update({
            '__builtins__': None,
            'self': self._obj,
        })

        out = self._obj_strings.get(string, None)\
            or self._cls_strings.get(string, None)\
            or string

        formatted = self.formatter.format(out, **ctx)
        return formatted
