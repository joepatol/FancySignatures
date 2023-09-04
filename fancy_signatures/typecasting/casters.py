from typing import TypeAlias

from ..core.interface import TypeCaster


_STRICT_CUSTOM_HANDLERS: dict[TypeAlias, TypeCaster] = {}  # Type should exactly match 
_CUSTOM_HANDLERS: dict[TypeAlias, TypeCaster] = {}  # Exact match or subclass


def register_handler(type_hint: TypeAlias, handler: TypeCaster, strict: bool) -> None:
    if strict:
        _STRICT_CUSTOM_HANDLERS[type_hint] = handler
    else:
        _CUSTOM_HANDLERS[type_hint] = handler
