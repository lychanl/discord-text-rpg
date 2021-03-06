from typing import Collection, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.data.loaders.attribute_loader import AttributeLoader


class QualifierError(Exception):
    pass


class QualifierCheckFailed(Exception):
    pass


class Qualifier:
    @property
    def collection_only(self):
        return False


class NumberQualifier(Qualifier):
    def __init__(self, mn: int, mx: Optional[int]):
        assert not mx or mn <= mx
        super(NumberQualifier, self).__init__()

        self._mn = mn
        self._mx = mx

    @property
    def collection_only(self) -> bool:
        return self._mx and self._mx > 1

    def check(self, num: int) -> None:
        if not (self._mn <= num):
            raise QualifierCheckFailed('Number qualifier check failed')
        if self._mx and not (num <= self._mx):
            raise QualifierCheckFailed('Number qualifier check failed')


class Qualifiers:
    def __init__(self, *qualifiers: Collection[Qualifier]):
        self._number_qualifier = None

        for qualifier in qualifiers:
            if isinstance(qualifier, NumberQualifier):
                if self._number_qualifier:
                    raise QualifierError('Multiple number qualifiers')
                self._number_qualifier = qualifier
            else:
                raise TypeError

        if not self._number_qualifier:
            self._number_qualifier = NumberQualifier(0, None)

    @property
    def collection_only(self) -> bool:
        return self._number_qualifier.collection_only

    def check(self, values: Collection['AttributeLoader']):
        self._number_qualifier.check(len(values))
