from typing import Any

from ..core.interface import TypeCaster


def handle_user_types(type_hint: type) -> TypeCaster:
    def _handler_func(value: Any) -> Any:
        if isinstance(value, type_hint):
            return value
        if isinstance(value, dict):
            return type_hint(**value)
        if isinstance(value, (tuple, list)):
            return type_hint(*value)
        return type_hint(value)
    return TypeCaster(_handler_func)
