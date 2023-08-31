from typing import TypeVar, Any, Generic
from abc import ABC, abstractmethod

from .types import TypeCastFunc


T = TypeVar("T")


class TypeCaster:
    def __init__(self, handler: TypeCastFunc) -> None:
        self._handler = handler
    
    def __call__(self, param_value: Any) -> Any:
        return self._handler(param_value)


class Validator(Generic[T], ABC):
    @abstractmethod
    def __call__(self, name: str, obj: T) -> T: ...


class Default(Generic[T], ABC):
    @abstractmethod
    def __call__(self, value: Any) -> T: ...
