from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.data.locale.localized_object import LocalizedObject


def plurals_group(objects: Iterable['LocalizedObject'], name: str, plural: str):
    plurals = {}
    counts = {}

    for o in objects:
        nm = o.strings[name]
        if nm in counts:
            counts[nm] += 1
        else:
            counts[nm] = 1
            plurals[nm] = o.strings[plural]

    return {nm if count == 1 else plurals[nm]: count for nm, count in counts.items()}
