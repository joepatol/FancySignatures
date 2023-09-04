from typing import Any, TypeVar, Callable

from fancy_signatures.core.types import __EmptyArg__

from ..core.interface import Default
from ..core.types import __EmptyArg__


T = TypeVar("T")
FactoryFunc = Callable[[], Any]


class DefaultValue(Default[T]):
    def __init__(self, value: Any = __EmptyArg__()) -> None:
        self._value = value
        
    def get(self, value: T) -> T:
        if isinstance(value, __EmptyArg__):
            return self._value
        return value


class IntDefault(DefaultValue[int]): pass
class FloatDefault(DefaultValue[float]): pass
class StringDefault(DefaultValue[str]): pass


class DefaultFactory(Default[T]):
    def __init__(self, factory_func: FactoryFunc = __EmptyArg__) -> None:
        self._factory = factory_func
    
    def get(self, value: T) -> T:
        if isinstance(value, __EmptyArg__):
            return self._factory()
        return value


ListDefault: DefaultFactory[list] = DefaultFactory(list)
DictDefault: DefaultFactory[dict] = DefaultFactory(dict)
TupleDefault: DefaultFactory[tuple] = DefaultFactory(tuple)
SetDefault: DefaultFactory[set] = DefaultFactory(set)
