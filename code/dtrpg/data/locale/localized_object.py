from datetime import datetime, timedelta
from dtrpg.data.locale.formatter import LocaleFormatter
import dtrpg.data.locale.helpers as helpers

from typing import Mapping, Tuple, Union


class DuplicateStringError(Exception):
    pass


class LocalizedObject:
    _class_strings = {}
    default_parser = None

    @classmethod
    def get_class_strings(cls) -> Mapping[str, str]:
        if cls not in cls._class_strings:
            cls._class_strings[cls] = {}
        return cls._class_strings[cls]

    def __init__(self):
        self.id = None
        self.factory_id = None
        self._obj_strings = {}
        self._strings_mapper = ObjectStrings(self._obj_strings, self.get_class_strings(), self)

    @property
    def strings(self) -> Mapping[str, str]:
        return self._strings_mapper

    @classmethod
    def add_class_string(cls, string: str, value: str) -> None:
        class_strings = cls.get_class_strings()
        if string in class_strings:
            raise DuplicateStringError
        class_strings[string] = value

    def add_string(self, string: str, value: str) -> None:
        if string in self._obj_strings:
            raise DuplicateStringError
        self._obj_strings[string] = value

    def finalize_locale(self) -> None:
        pass


class LocalizedObjectFactory(LocalizedObject):
    def __init__(self, clss: type):
        super().__init__()
        self._cls = clss

    def _create(self, *args: list, **kwargs: dict) -> LocalizedObject:
        obj = self._cls(*args, **kwargs)
        obj._obj_strings.update(self._obj_strings)
        obj.factory_id = self.id
        return obj

    def create(self) -> LocalizedObject:
        return self._create()


class ObjectStrings:
    AVAILABLE_BUILTINS = {
        'int': int, 'float': float, 'str': str, 'abs': abs,
        'len': len, 'sum': sum, 'any': any, 'all': all, 'enumerate': enumerate, 'zip': zip,
        'colon': ':',
        'datetime': datetime, 'timedelta': timedelta,
        'helpers': helpers}

    formatter = LocaleFormatter()

    def __init__(self, obj_strings: Mapping[str, str], cls_strings: Mapping[str, str], obj: LocalizedObject):
        self._obj_strings = obj_strings
        self._cls_strings = cls_strings
        self._obj = obj

    def get(self, string: str, ctx: Tuple[str, dict] = None, default: str = None) -> str:
        if ctx is None:
            ctx = {}

        if default is None:
            default = string

        ctx.update({
            '__builtins__': self.AVAILABLE_BUILTINS,
            'self': self._obj,
        })

        out = self._obj_strings.get(string, self._cls_strings.get(string, default))

        formatted = self.formatter.format(out, **ctx)
        return formatted

    def __getitem__(self, args: Union[str, Tuple[str, dict]]) -> str:
        if isinstance(args, str):
            string = args
            ctx = {}
        else:
            string, ctx = args
            ctx = dict(ctx)

        return self.get(string, ctx)

    def __contains__(self, item: object) -> bool:
        return item in self._obj_strings or item in self._cls_strings
