from typing import Protocol, TypeVar, Any, Self

from ..core.interface import Validator
from ..core.exceptions import ValidationError


class HasLength(Protocol):
    def __len__(self) -> int:
        ...


class HasMin(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...


class HasEq(Protocol):
    def __eq__(self, other: Any) -> bool:
        ...


class HasMax(Protocol):
    def __gt__(self, other: Any) -> bool:
        ...


class IsIterable(Protocol):
    def __iter__(self) -> Any:
        ...

    def __next__(self) -> Any:
        ...


class HasLe(HasMin, HasEq, Protocol):
    ...


class HasGe(HasMax, HasEq, Protocol):
    ...


class HasMinMax(HasMax, HasMin, HasEq, Protocol):
    ...


class SizedIterable(IsIterable, HasLength, Protocol):
    ...


T = TypeVar("T")
U = TypeVar("U")
MinT = TypeVar("MinT", bound=HasLe)
MaxT = TypeVar("MaxT", bound=HasGe)
LengthT = TypeVar("LengthT", bound=HasLength)
SizedIterableT = TypeVar("SizedIterableT", bound=SizedIterable)


class ValidateContentMixin:  # This is ugly.. improve later
    def content(self, *validators: Validator) -> Self:
        self._content_validators = validators
        return self

    def _validate_content(self, name: str, obj: IsIterable) -> None:
        if hasattr(self, "_content_validators"):
            for v in self._content_validators:
                for el in obj:
                    v(name, el)


class Min(Validator[MinT]):
    def __init__(self, value: MinT) -> None:
        self._min = value

    def validate(self, name: str, obj: MinT) -> MinT:
        if obj < self._min:
            raise ValidationError(f"Value(s) should be greater than {self._min}", name)
        return obj


class Max(Validator[MaxT]):
    def __init__(self, value: MaxT) -> None:
        self._max = value

    def validate(self, name: str, obj: MaxT) -> MaxT:
        if obj > self._max:
            raise ValidationError(f"Value(s) should be smaller than {self._max}", name)
        return obj


class IntMin(Min[int]):
    pass


class FloatMin(Min[float]):
    pass


class NumericMin(Min[float | int]):
    pass


class IntMax(Max[int]):
    pass


class FloatMax(Max[float]):
    pass


class NumericMax(Max[float | int]):
    pass


class StrLength(Validator[str]):
    def __init__(self, min: int | None = None, max: int | None = None):
        self._min = min
        self._max = max

    def validate(self, name: str, obj: str) -> str:
        if self._min and len(obj) < self._min:
            raise ValidationError("String is to short.", name)
        if self._max and len(obj) > self._max:
            raise ValidationError("String too long", name)
        return obj


class MaxLength(Validator[SizedIterable], ValidateContentMixin):
    def __init__(self, max: int) -> None:
        self._max = max

    def validate(self, name: str, obj: SizedIterable) -> SizedIterable:
        if len(obj) > self._max:
            raise ValidationError("Length too large", name)
        self._validate_content(name, obj)
        return obj


class MinLength(Validator[SizedIterable], ValidateContentMixin):
    def __init__(self, min: int) -> None:
        self._min = min

    def validate(self, name: str, obj: SizedIterable) -> SizedIterable:
        if len(obj) < self._min:
            raise ValidationError("Length too small", name)
        self._validate_content(name, obj)
        return obj
