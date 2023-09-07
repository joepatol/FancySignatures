from typing import Any, get_args, Union
from types import UnionType

from ..core.exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory
from .handlers import register_handler


class UnionTypeCaster(TypeCaster[UnionType]):
    def __init__(self, expected_type: Any) -> None:
        super().__init__(expected_type)
        self._origins = get_args(expected_type)

    def validate(self, param_value: Any) -> bool:
        for origin in self._origins:
            if typecaster_factory(origin).validate(param_value):
                return True
        return False

    def cast(self, param_value: Any) -> UnionType:
        for origin in self._origins:
            try:
                return typecaster_factory(origin).cast(param_value)
            except TypeCastError:
                pass
        raise TypeCastError(self._origins)


register_handler(type_hints=[Union, UnionType], handler=UnionTypeCaster, strict=True)
