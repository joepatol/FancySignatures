from typing import Any

from ..core.interface import TypeCaster
from ..core.exceptions import TypeValidationError


def handle_other_types(type_hint: type) -> TypeCaster:
    def _handler_func(value: Any, strict: bool) -> Any:
        if isinstance(value, type_hint):
            return value
        if strict:
            raise TypeValidationError(f"Invalid type, should be {type_hint}")
        # String is a specials case, e.g. list could also be cast to str.
        if type_hint == str:
            return str(value)
        if isinstance(value, dict):
            return type_hint(**value)
        if isinstance(value, (tuple, list)):
            return type_hint(*value)
        return type_hint(value)
    return TypeCaster(_handler_func)
