from typing import Any

from ..core.interface import TypeCaster
from ..exceptions import TypeCastError


class DefaultTypeCaster(TypeCaster[Any]):
    """Default typecaster. If no TypeCaster implementation is found this is the fallback.

    Check if the parameter value is a dict, tuple or list. If so try to unpack.
    Otherwise call `self._type_hint` with the given parameter.
    """

    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, self._type_hint)

    def cast(self, param_value: Any) -> Any:
        try:
            if isinstance(param_value, dict):
                return self._type_hint(**param_value)
            if isinstance(param_value, (tuple, list)):
                return self._type_hint(*param_value)
            return self._type_hint(param_value)
        except (TypeError, ValueError):
            raise TypeCastError(self._type_hint)
