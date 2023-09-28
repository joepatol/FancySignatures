from typing import Any

from ..core.interface import TypeCaster
from ..exceptions import TypeCastError


class DefaultTypeCaster(TypeCaster[Any]):
    """Default typecaster. If no TypeCaster implementation is found this is the fallback.

    Check if the parameter value is a dict, tuple or list. If so try to unpack.
    Otherwise call `self._type_hint` with the given parameter.
    """

    def validate(self, param_value: Any) -> bool:
        # If there is an origin, we check against that. Subscripted generics
        # cannot be used for instance checks.
        if hasattr(self._type_hint, "__origin__"):
            return isinstance(param_value, self._type_hint.__origin__)
        return isinstance(param_value, self._type_hint)

    def cast(self, param_value: Any) -> Any:
        try:
            if isinstance(param_value, dict):
                return self._type_hint(**param_value)
            if isinstance(param_value, (tuple, list)):
                return self._type_hint(*param_value)
            return self._type_hint(param_value)
        except (TypeError, ValueError) as e:
            raise TypeCastError(self._type_hint, extra_info=str(e))


class IntOrFloatTypeCaster(TypeCaster[int | float]):
    """Caster for integers and floats, to make the errors a bit more specific
    as opposed to DefaultTypeCaster
    """

    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, self._type_hint)

    def cast(self, param_value: Any) -> int | float:
        try:
            return self._type_hint(param_value)
        except (ValueError, TypeError) as e:
            raise TypeCastError(self._type_hint, extra_info=str(e))
