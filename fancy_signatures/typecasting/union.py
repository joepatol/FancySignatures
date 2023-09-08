from typing import Any, get_args
from types import UnionType

from ..exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory


class UnionTypeCaster(TypeCaster[UnionType]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._origins = get_args(type_hint)

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
