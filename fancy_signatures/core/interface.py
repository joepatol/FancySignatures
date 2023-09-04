from typing import TypeVar, Any, Generic, TypeAlias
from abc import ABC, abstractmethod

from .exceptions import TypeValidationError


T = TypeVar("T")


class Validator(Generic[T], ABC):
    @abstractmethod
    def validate(self, name: str, obj: T) -> T: ...
    def __call__(self, name: str, obj: T) -> T: 
        return self.validate(name, obj)


class Default(Generic[T], ABC):
    @abstractmethod
    def get(self, value: Any) -> T: ...
    def __call__(self, value: Any) -> T: 
        return self.get(value)


class TypeCaster(Generic[T], ABC):
    def __init__(self, expected_type: TypeAlias) -> None:
        self._type = expected_type 
    @abstractmethod
    def validate(self, param_value: Any) -> bool: ...
    @abstractmethod
    def cast(self, param_value: Any) -> T: ...
    def __call__(self, param_value: Any, strict: bool) -> Any:
        if not self.validate(param_value):
            if strict: raise TypeValidationError(f"Invalid type, should be {self._type}")
            else: return self.cast(param_value)
        return param_value
