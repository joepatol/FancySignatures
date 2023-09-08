from typing import Protocol, TypeVar, Any
import re
import decimal

from ..core.interface import Validator
from ..exceptions import ValidatorFailed
from .mixins import AllowOptionalMixin


class HasLength(Protocol):  # pragma: no cover
    def __len__(self) -> int:
        ...


class HasLT(Protocol):  # pragma: no cover
    def __lt__(self, other: Any) -> bool:
        ...


class HasEq(Protocol):  # pragma: no cover
    def __eq__(self, other: Any) -> bool:
        ...


class HasGT(Protocol):  # pragma: no cover
    def __gt__(self, other: Any) -> bool:
        ...


class IsIterable(Protocol):  # pragma: no cover
    def __iter__(self) -> Any:
        ...

    def __next__(self) -> Any:
        ...


class HasLe(HasLT, HasEq, Protocol):  # pragma: no cover
    ...


class HasGe(HasGT, HasEq, Protocol):  # pragma: no cover
    ...


class HasMinMax(HasLT, HasGT, HasEq, Protocol):  # pragma: no cover
    ...


T = TypeVar("T")
U = TypeVar("U")
GtT = TypeVar("GtT", bound=HasGT)
LtT = TypeVar("LtT", bound=HasLT)
GeT = TypeVar("GeT", bound=HasGe)
LeT = TypeVar("LeT", bound=HasLe)
LengthT = TypeVar("LengthT", bound=HasLength)


class GE(Validator[LtT]):
    def __init__(self, value: Any) -> None:
        self._min = value

    def validate(self, obj: LtT) -> LtT:
        if obj < self._min:
            raise ValidatorFailed(f"Value should be greater than or equal to {self._min}")
        return obj


class GT(Validator[LeT]):
    def __init__(self, value: Any) -> None:
        self._min = value

    def validate(self, obj: LeT) -> LeT:
        if obj <= self._min:
            raise ValidatorFailed(f"Value should be greater than {self._min}")
        return obj


class LE(Validator[GtT]):
    def __init__(self, value: Any) -> None:
        self._max = value

    def validate(self, obj: GtT) -> GtT:
        if obj > self._max:
            raise ValidatorFailed(f"Value should be smaller than {self._max}")
        return obj


class LT(Validator[GeT]):
    def __init__(self, value: Any) -> None:
        self._max = value

    def validate(self, obj: GeT) -> GeT:
        if obj >= self._max:
            raise ValidatorFailed(f"Value should be smaller than or equal to {self._max}")
        return obj


class MaxLength(Validator[LengthT]):
    def __init__(self, max: int) -> None:
        self._max = max

    def validate(self, obj: LengthT) -> LengthT:
        if len(obj) > self._max:
            raise ValidatorFailed("Length too large")
        return obj


class MinLength(Validator[LengthT]):
    def __init__(self, min: int) -> None:
        self._min = min

    def validate(self, obj: LengthT) -> LengthT:
        if len(obj) < self._min:
            raise ValidatorFailed("Length too small")
        return obj


class BlackListedValues(Validator[T]):
    def __init__(self, *values: T) -> None:
        self._not_allowed = values

    def validate(self, obj: T) -> T:
        if obj in self._not_allowed:
            raise ValidatorFailed("Value is blacklisted")
        return obj


class IsInValidator(Validator[T]):
    def __init__(self, *values: T) -> None:
        self._values = values

    def validate(self, obj: T) -> T:
        if obj not in self._values:
            raise ValidatorFailed(f"Invalid value, should be one of '{self._values}'")
        return obj


class RegexValidator(Validator[str]):
    def __init__(self, pattern: str) -> None:
        self._pattern = pattern

    def validate(self, obj: str) -> str:
        if not re.match(self._pattern, obj):
            raise ValidatorFailed(f"Parameter should match the regex '{self._pattern}'")
        return obj


class MultipleOfValidator(Validator[int | float]):
    def __init__(self, base: int | float) -> None:
        self._base = base

    def validate(self, obj: int | float) -> int | float:
        if obj % self._base != 0:
            raise ValidatorFailed(f"Parameter should be a multiple of {self._base}")
        return obj


class DecimalPlacesValidator(Validator[float]):
    def __init__(self, places: int) -> None:
        self._places = places

    def validate(self, obj: float) -> float:
        try:
            places = decimal.Decimal(str(obj)).as_tuple().exponent
        except decimal.InvalidOperation:
            raise TypeError("Value cannot be converted to a decimal")
        assert isinstance(places, int)  # for mypy
        if -places > self._places:
            raise ValidatorFailed(f"Parameter should have a maximum of {self._places} decimal places")
        return obj


class OptionalGE(AllowOptionalMixin, GE[LtT]):
    pass


class OptionalGT(AllowOptionalMixin, GT[LeT]):
    pass


class OptionalLE(AllowOptionalMixin, LE[GtT]):
    pass


class OptionalLT(AllowOptionalMixin, LT[GeT]):
    pass


class OptionalRegexValidator(AllowOptionalMixin, RegexValidator):
    pass


class OptionalMultipleOfValidator(AllowOptionalMixin, MultipleOfValidator):
    pass


class OptionalDecimalPlacesValidator(AllowOptionalMixin, DecimalPlacesValidator):
    pass
