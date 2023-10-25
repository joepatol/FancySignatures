from typing import Any, get_origin, get_args, TypeVar, Sequence, Mapping

from ..exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory
from ..settings import Settings


ELLIPSIS = ...

T = TypeVar("T", set, dict, tuple, list)


class SequenceTypeCaster(TypeCaster[Sequence]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._origin = get_origin(type_hint) or type_hint  # type: ignore
        # If we just expect a sequence, default to list
        if self._origin == Sequence:
            self._origin = list
        _args = get_args(type_hint)
        arg_hint = _args[0] if len(_args) > 0 else Any
        self._arg_typecaster = typecaster_factory(arg_hint)

    def validate(self, param_value: Any) -> bool:
        if issubclass(type(param_value), self._origin):
            if all([self._arg_typecaster.validate(val) for val in param_value]):
                return True
        return False

    def cast(self, param_value: Any) -> Sequence:
        casted_value = _attempt_typecast(param_value, self._origin)  # type: ignore
        return self._origin([self._arg_typecaster.cast(x) for x in casted_value])


class TupleTypeCaster(TypeCaster[tuple]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        args = get_args(type_hint)
        self._allow_additional = args[-1] == ELLIPSIS if len(args) > 0 else True
        self._arg_typecasters = [typecaster_factory(arg) for arg in args]

    def _validate_length(self, tuple_length: int) -> bool:
        if Settings.ALLOW_TUPLE_ADDITIONAL_PARAMS or self._allow_additional:
            return True
        return tuple_length == len(self._arg_typecasters)

    def validate(self, param_value: Any) -> bool:
        if not issubclass(type(param_value), tuple):
            return False
        elif not self._validate_length(len(param_value)):
            return False
        # Consider the length of the typecaster, i.e. we allow a tuple with additonal parameters
        elif all([self._arg_typecasters[i].validate(param_value[i]) for i in range(len(self._arg_typecasters))]):
            return True
        return False

    def cast(self, param_value: Any) -> tuple:
        casted_value = _attempt_typecast(param_value, tuple)  # type: ignore
        if not self._validate_length(len(casted_value)):
            raise TypeCastError(self._type_hint)

        # If we're here, lengths match or it's allowed to have extra params
        # So iterate over values and create a typecaster if it was not typehinted
        result: list[Any] = []
        i: int = 0
        while i < len(casted_value):
            try:
                value_typecaster = self._arg_typecasters[i]
            except IndexError:
                value_typecaster = typecaster_factory(Any)

            result.append(value_typecaster.cast(casted_value[i]))
            i += 1

        return tuple(result)


class MappingTypeCaster(TypeCaster[Mapping]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._origin = get_origin(type_hint)
        # Default to dict
        if self._origin == Mapping:
            self._origin = dict
        next_hint = get_args(type_hint)
        key_hint = next_hint[0] if len(next_hint) > 0 else Any
        value_hint = next_hint[1] if len(next_hint) > 0 else Any
        self._key_caster = typecaster_factory(key_hint)
        self._value_caster = typecaster_factory(value_hint)

    def validate(self, param_value: Any) -> bool:
        if isinstance(param_value, dict):
            keys = [self._key_caster.validate(value) for value in param_value.keys()]
            values = [self._value_caster.validate(value) for value in param_value.values()]
            if all(keys + values):
                return True
        return False

    def cast(self, param_value: Any) -> Mapping:
        casted_value = _attempt_typecast(param_value, self._origin)
        return {self._key_caster.cast(k): self._value_caster.cast(v) for k, v in casted_value.items()}


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
