from typing import Any, TypeVar, Callable

from ..core.interface import Default
from ..core.empty import is_empty, __EmptyArg__


T = TypeVar("T")
FactoryFunc = Callable[[], Any]


class DefaultValue(Default[T]):
    def __init__(self, value: Any = __EmptyArg__()) -> None:
        self._value = value

    def get(self, value: T) -> T:
        if is_empty(value):
            return self._value
        return value


class DefaultFactory(Default[T]):
    def __init__(self, factory_func: FactoryFunc = __EmptyArg__) -> None:
        self._factory = factory_func

    def get(self, value: T) -> T:
        if is_empty(value):
            return self._factory()
        return value


Zero: DefaultValue[int] = DefaultValue(0)
EmptyList: DefaultFactory[list] = DefaultFactory(list)
EmptyDict: DefaultFactory[dict] = DefaultFactory(dict)
EmptyTuple: DefaultFactory[tuple] = DefaultFactory(tuple)
EmptySet: DefaultFactory[set] = DefaultFactory(set)
