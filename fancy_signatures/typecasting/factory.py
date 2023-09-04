from typing import get_origin, TypeAlias

from ..core.interface import TypeCaster
from .origins import OriginsTypeCaster
from .casters import _STRICT_CUSTOM_HANDLERS, _CUSTOM_HANDLERS


def typecaster_factory(type_hint: TypeAlias) -> TypeCaster:
    raw_origin = get_origin(type_hint)
    origin = raw_origin if raw_origin is not None else type_hint
    
    if origin in _STRICT_CUSTOM_HANDLERS:
        return _STRICT_CUSTOM_HANDLERS[origin](type_hint)

    for type_for_handler in _CUSTOM_HANDLERS:
        if issubclass(origin, type_for_handler):
            return _CUSTOM_HANDLERS[type_for_handler](type_hint)
    
    return OriginsTypeCaster(expected_type=origin)
