from typing import Any, get_args
from typing_extensions import _AnnotatedAlias

from ..core.exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory


class StringTypeCaster(TypeCaster[str]):
    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, str)

    def cast(self, param_value: Any) -> str:
        try:
            return str(param_value)
        except TypeError:
            raise TypeCastError(str)


class AnyTypeCaster(TypeCaster[Any]):
    def validate(self, _: Any) -> bool:
        return True

    def cast(self, param_value: Any) -> Any:
        return param_value


class AnnotatedTypeCaster(TypeCaster[_AnnotatedAlias]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._origin = get_args(type_hint)[0]

    def validate(self, param_value: Any) -> bool:
        return typecaster_factory(self._origin).validate(param_value)

    def cast(self, param_value: Any) -> Any:
        return typecaster_factory(self._origin).cast(param_value)


class BooleanTypeCaster(TypeCaster[bool]):
    _TRUE = [1, "1", "1.0", 1.0, "true", True]
    _FALSE = [0, "0", "0.0", 0.0, "false", False]

    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, bool)

    def cast(self, param_value: Any) -> bool:
        if isinstance(param_value, str):
            param_value = param_value.lower()
        if param_value in self._TRUE:
            return True
        elif param_value in self._FALSE:
            return False
        raise TypeCastError(bool)


class NoneTypeCaster(TypeCaster[None]):
    def validate(self, param_value: Any) -> bool:
        return param_value is None

    def cast(self, param_value: Any) -> None:
        if isinstance(param_value, str):
            try:
                param_value = eval(param_value)
            except TypeError:
                raise TypeCastError(type(None))
        if not self.validate(param_value):
            raise TypeCastError(type(None))
