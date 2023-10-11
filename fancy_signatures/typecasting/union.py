from typing import Any, get_args
from types import UnionType

from ..exceptions import TypeCastError
from ..core.interface import TypeCaster
from .factory import typecaster_factory


class UnionTypeCaster(TypeCaster[UnionType]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        origins = get_args(type_hint)
        self._origin_casters = [typecaster_factory(origin) for origin in origins]

    def validate(self, param_value: Any) -> bool:
        for typecaster in self._origin_casters:
            if typecaster.validate(param_value):
                return True
        return False

    def cast(self, param_value: Any) -> UnionType:
        for typecaster in self._origin_casters:
            try:
                return typecaster.cast(param_value)
            except TypeCastError:
                pass
        raise TypeCastError(self._type_hint)
