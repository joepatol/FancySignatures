from typing import TypeAlias, Type

from ..core.interface import TypeCaster


_STRICT_CUSTOM_HANDLERS: dict[TypeAlias, Type[TypeCaster]] = {}  # Type should exactly match 
_CUSTOM_HANDLERS: dict[TypeAlias, Type[TypeCaster]] = {}  # Exact match or subclass


def register_handler(type_hints: list[TypeAlias], handler: Type[TypeCaster], strict: bool) -> None:
    if strict:
        for hint in type_hints:
            _STRICT_CUSTOM_HANDLERS[hint] = handler
    else:
        for hint in type_hints:
            _CUSTOM_HANDLERS[hint] = handler
