import difflib
import re
from typing import Any, Iterable, Type

import lark
from dtrpg.data.locale.localized_object import LocalizedObject


class ArgumentError(Exception):
    def __init__(self, value: str):
        super().__init__()
        self.value = value


class ParserError(Exception):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class ParsingError(Exception):
    def __init__(self, text: str, lark_exception: lark.exceptions.UnexpectedInput) -> None:
        super().__init__()

        self.exception = lark_exception
        self.matched_line, self.unmatched = self._hint_base(lark_exception)
        self.hints = [(r, self.matched_line + h) for r, h in self._hints(
            self.unmatched,
            lark_exception.allowed if hasattr(lark_exception, 'allowed') else lark_exception.expected
        )]

    def _hint_base(self, text, lp, cp):
        line = text.splitlines()[lp - 1]
        parsed = line[:cp - 1]
        unparsed = line[cp - 1:]
        return parsed, unparsed

    def _hints(self, unparsed, allowed):
        return list(reversed(sorted(
            (difflib.SequenceMatcher(None, unparsed.lower(), possibility.lower()).ratio(), possibility.lower())
            for possibility in allowed
        )))


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
