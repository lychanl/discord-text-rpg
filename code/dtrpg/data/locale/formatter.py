import string
from typing import Dict, Tuple


class LocaleFormatter(string.Formatter):
    def get_field(self, field: str, args: list, kwargs: Dict[str, object]) -> Tuple[object, None]:
        return eval(field, kwargs), None
