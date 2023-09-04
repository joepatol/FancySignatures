from typing import Any, get_args, Annotated
from typing_extensions import _AnnotatedAlias

from ..core.interface import TypeCaster
from .factory import typecaster_factory
from .casters import register_handler


class StringTypeCaster(TypeCaster[str]):
    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, str)

    def cast(self, param_value: Any) -> str:
        return str(param_value)


class AnyTypeCaster(TypeCaster[Any]):
    def validate(self, _: Any) -> bool:
        return True

    def cast(self, param_value: Any) -> Any:
        return param_value


class AnnotatedTypeCaster(TypeCaster[_AnnotatedAlias]):
    def __init__(self, expected_type: _AnnotatedAlias) -> None:
        super().__init__(get_args(expected_type)[0])

    def validate(self, param_value: Any) -> bool:
        return typecaster_factory(self._type).validate(param_value)

    def cast(self, param_value: Any) -> Any:
        return typecaster_factory(self._type).cast(param_value)


register_handler(type_hints=[str], handler=StringTypeCaster, strict=True)
register_handler(type_hints=[Any], handler=AnyTypeCaster, strict=True)
register_handler(type_hints=[Annotated], handler=AnnotatedTypeCaster, strict=True)
