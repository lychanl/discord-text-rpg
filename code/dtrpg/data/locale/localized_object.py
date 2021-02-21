from dtrpg.data.locale.formatter import LocaleFormatter

from typing import Mapping, Tuple, Union


class DuplicateStringError(Exception):
    pass


class LocalizedObject:
    _class_strings = {}

    @classmethod
    def _get_class_strings(cls) -> Mapping[str, str]:
        if cls not in cls._class_strings:
            cls._class_strings[cls] = {}
        return cls._class_strings[cls]

    def __init__(self):
        self._obj_strings = {}
        self._strings_mapper = ObjectStrings(self._obj_strings, self._get_class_strings(), self)

    @property
    def strings(self) -> Mapping[str, str]:
        return self._strings_mapper

    @classmethod
    def add_class_string(cls, string: str, value: str) -> None:
        class_strings = cls._get_class_strings()
        if string in class_strings:
            raise DuplicateStringError
        class_strings[string] = value

    def add_string(self, string: str, value: str) -> None:
        if string in self._obj_strings:
            raise DuplicateStringError
        self._obj_strings[string] = value


class LocalizedObjectFactory(LocalizedObject):
    def __init__(self, clss: type):
        super().__init__()
        self._cls = clss

    def _create(self) -> LocalizedObject:
        obj = self._cls()
        obj._obj_strings.update(self._obj_strings)
        return obj

    def create(self) -> LocalizedObject:
        return self._create()


class ObjectStrings:
    AVAILABLE_BUILTINS = {
        'int': int, 'float': float, 'str': str, 'abs': abs,
        'len': len, 'sum': sum, 'any': any, 'all': all, 'zip': zip}

    formatter = LocaleFormatter()

    def __init__(self, obj_strings: Mapping[str, str], cls_strings: Mapping[str, str], obj: LocalizedObject):
        self._obj_strings = obj_strings
        self._cls_strings = cls_strings
        self._obj = obj

    def get(self, string: str, ctx: Tuple[str, dict]=None, default: str = None) -> str:
        if ctx is None:
            ctx = {}

        if default is None:
            default = string

        ctx.update({
            '__builtins__': self.AVAILABLE_BUILTINS,
            'self': self._obj,
        })

        out = self._obj_strings.get(string, None)\
            or self._cls_strings.get(string, None)\
            or default

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
