from typing import TypeVar, Any, Generic
from abc import ABC, abstractmethod

from ..exceptions import TypeValidationError, ValidationError, ValidatorFailed, TypeCastError


T = TypeVar("T")


class Validator(Generic[T], ABC):
    @abstractmethod
    def validate(self, obj: T) -> T:  # pragma: no cover
        ...

    def __call__(self, name: str, obj: T) -> T:
        try:
            return self.validate(obj)
        except ValidatorFailed as e:
            raise ValidationError(str(e), name)


class Default(Generic[T], ABC):
    @abstractmethod
    def get(self, value: Any) -> T:  # pragma: no cover
        ...

    def __call__(self, value: Any) -> T:
        return self.get(value)


class TypeCaster(Generic[T], ABC):
    def __init__(self, type_hint: Any) -> None:
        self._type_hint = type_hint

    @abstractmethod
    def validate(self, param_value: Any) -> bool:  # pragma: no cover
        ...

    @abstractmethod
    def cast(self, param_value: Any) -> T:  # pragma: no cover
        ...

    def __call__(self, param_value: Any, strict: bool) -> T:
        if not self.validate(param_value):
            if strict:
                raise TypeValidationError(f"Invalid type, should be {self._type_hint}")
            else:
                try:
                    return self.cast(param_value)
                except TypeCastError:
                    raise TypeCastError(self._type_hint)
        return param_value
