from typing import Any, get_origin, get_args, cast, Type

from ..core.interface import TypeCaster
from .factory import typecaster_factory
from .handlers import register_handler


class ListTupleSetTypeCaster(TypeCaster[list | tuple | set]):
    def __init__(self, expected_type: type[list | tuple | set]) -> None:
        super().__init__(expected_type)
        self._origin: Type = cast(Type[list] | Type[tuple] | Type[set], get_origin(expected_type) or expected_type)
        _args = get_args(expected_type)
        self._arg = get_args(expected_type)[0] if len(_args) > 0 else Any

    def validate(self, param_value: Any) -> bool:
        if issubclass(type(param_value), self._origin):
            if all([typecaster_factory(self._arg).validate(val) for val in param_value]):
                return True
        return False

    def cast(self, param_value: Any) -> list | tuple | set:
        if isinstance(param_value, str):
            param_value = eval(param_value)
        casted_value = self._origin(param_value)
        return self._origin([typecaster_factory(self._arg).cast(x) for x in casted_value])


class DictTypeCaster(TypeCaster[dict]):
    def __init__(self, expected_type: type[dict]) -> None:
        super().__init__(expected_type)
        next_hint = get_args(self._type)
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
        if isinstance(param_value, str):
            param_value = eval(param_value)
        casted_value = dict(param_value)
        return {
            typecaster_factory(self._key_hint).cast(k): typecaster_factory(self._value_hint).cast(v)
            for k, v in casted_value.items()
        }


register_handler(type_hints=[list, tuple, set], handler=ListTupleSetTypeCaster, strict=False)
register_handler(type_hints=[dict], handler=DictTypeCaster, strict=True)
