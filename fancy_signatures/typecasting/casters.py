from typing import TypeAlias, Type

from ..core.interface import TypeCaster


_STRICT_CUSTOM_HANDLERS: dict[TypeAlias, Type[TypeCaster]] = {}  # Type should exactly match 
_CUSTOM_HANDLERS: dict[TypeAlias, Type[TypeCaster]] = {}  # Exact match or subclass


def register_handler(type_hints: list[TypeAlias], handler: Type[TypeCaster], strict: bool) -> None:
    """Register a TypeCaster object that handles a set of type hints.

    Args:
        type_hints (list[TypeAlias]): the type hints supported by this handler
        handler (Type[TypeCaster]): the TypeCaster to handle the value
        strict (bool): Whether the caster is invoked only if the type matches exactly (True)
        or if it's also invoked for all subclasses of type_hints
    """
    if strict:
        for hint in type_hints:
            _STRICT_CUSTOM_HANDLERS[hint] = handler
    else:
        for hint in type_hints:
            _CUSTOM_HANDLERS[hint] = handler
