from typing import Any, get_origin, get_args, TypeVar

from ..exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory


T = TypeVar("T", set, dict, tuple, list)


class ListTupleSetTypeCaster(TypeCaster[list | tuple | set]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._origin: type[set | list | tuple] = get_origin(type_hint) or type_hint  # type: ignore
        _args = get_args(type_hint)
        self._arg = get_args(type_hint)[0] if len(_args) > 0 else Any

    def validate(self, param_value: Any) -> bool:
        if issubclass(type(param_value), self._origin):
            if all([typecaster_factory(self._arg).validate(val) for val in param_value]):
                return True
        return False

    def cast(self, param_value: Any) -> list | tuple | set:
        casted_value = _attempt_typecast(param_value, self._origin)  # type: ignore
        return self._origin([typecaster_factory(self._arg).cast(x) for x in casted_value])


class DictTypeCaster(TypeCaster[dict]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        next_hint = get_args(type_hint)
        self._key_hint = next_hint[0] if len(next_hint) > 0 else Any
        self._value_hint = next_hint[1] if len(next_hint) > 0 else Any

    def validate(self, param_value: Any) -> bool:
        if isinstance(param_value, dict):
            keys = [typecaster_factory(self._key_hint).validate(value) for value in param_value.keys()]
            values = [typecaster_factory(self._value_hint).validate(value) for value in param_value.values()]
            if all(keys + values):
                return True
        return False

    def cast(self, param_value: Any) -> dict:
        casted_value = _attempt_typecast(param_value, dict)
        return {
            typecaster_factory(self._key_hint).cast(k): typecaster_factory(self._value_hint).cast(v)
            for k, v in casted_value.items()
        }


def _attempt_typecast(value: Any, to_type: type[T]) -> T:
    if isinstance(value, str):
        try:
            value = eval(value)
        except Exception:
            raise TypeCastError(to_type)
    try:
        casted_value = to_type(value)
    except TypeError:
        raise TypeCastError(to_type)
    return casted_value
