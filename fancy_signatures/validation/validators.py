from typing import Protocol, TypeVar, Any

from ..core.interface import Validator
from ..core.exceptions import ValidationError


class HasLength(Protocol):
    def __len__(self) -> int:
        ...


class HasLT(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...


class HasEq(Protocol):
    def __eq__(self, other: Any) -> bool:
        ...


class HasGT(Protocol):
    def __gt__(self, other: Any) -> bool:
        ...


class IsIterable(Protocol):
    def __iter__(self) -> Any:
        ...

    def __next__(self) -> Any:
        ...


class HasLe(HasLT, HasEq, Protocol):
    ...


class HasGe(HasGT, HasEq, Protocol):
    ...


class HasMinMax(HasLT, HasGT, HasEq, Protocol):
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

    def validate(self, name: str, obj: LtT) -> LtT:
        if obj < self._min:
            raise ValidationError(f"Value should be greater than or equal to {self._min}", name)
        return obj


class GT(Validator[LeT]):
    def __init__(self, value: Any) -> None:
        self._min = value

    def validate(self, name: str, obj: LeT) -> LeT:
        if obj <= self._min:
            raise ValidationError(f"Value should be greater than {self._min}", name)
        return obj


class LE(Validator[GeT]):
    def __init__(self, value: Any) -> None:
        self._max = value

    def validate(self, name: str, obj: GeT) -> GeT:
        if obj > self._max:
            raise ValidationError(f"Value should be smaller than {self._max}", name)
        return obj


class LT(Validator[GeT]):
    def __init__(self, value: Any) -> None:
        self._max = value

    def validate(self, name: str, obj: GeT) -> GeT:
        if obj >= self._max:
            raise ValidationError(f"Value should be smaller than or equal to {self._max}", name)
        return obj


class MaxLength(Validator[HasLength]):
    def __init__(self, max: int) -> None:
        self._max = max

    def validate(self, name: str, obj: HasLength) -> HasLength:
        if len(obj) > self._max:
            raise ValidationError("Length too large", name)
        return obj


class MinLength(Validator[HasLength]):
    def __init__(self, min: int) -> None:
        self._min = min

    def validate(self, name: str, obj: HasLength) -> HasLength:
        if len(obj) < self._min:
            raise ValidationError("Length too small", name)
        return obj


class BlackListedValues(Validator[T]):
    def __init__(self, *values: T) -> None:
        self._not_allowed = values

    def validate(self, name: str, obj: T) -> T:
        if obj in self._not_allowed:
            raise ValueError("Value is blacklisted")
        return obj
