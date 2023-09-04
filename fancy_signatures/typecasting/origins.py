from typing import Any

from ..core.interface import TypeCaster


class OriginsTypeCaster(TypeCaster[Any]):
    """Typecaster for type hints that don't have an origin
    e.g. int, str or a user defined type that doesn't inherit from typing.Generic 
    or is not subscipted
    """
    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, self._type)
    
    def cast(self, param_value: Any) -> int:
        if isinstance(param_value, dict):
            return self._type(**param_value)
        if isinstance(param_value, (tuple, list)):
            return self._type(*param_value)
        return self._type(param_value)
