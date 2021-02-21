from enum import Enum

from typing import Collection, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.data.loaders.type_loader import TypeLoader
    from dtrpg.data.locale.localized_object import LocalizedObject


class LocaleLoader:
    def __init__(self, rows: Collection[Mapping[str, str]]):
        self._locale_strings = {
            (row['object'], row['string']): row['value']
            for row in rows
        }

    def apply(self, world: Mapping[str, 'LocalizedObject'], loaders: Mapping[str, 'TypeLoader']) -> None:
        for (obj, string), value in self._locale_strings.items():
            if '.' in obj:
                enum, obj = obj.split('.')
                class_ = loaders[enum].class_
                assert issubclass(class_, Enum), "Nested objects names supported only for enums"
                class_[obj].add_string(string, value)
            else:
                if obj in world:
                    world[obj].add_string(string, value)
                else:
                    loaders[obj].class_.add_class_string(string, value)
