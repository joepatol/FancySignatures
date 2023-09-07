from typing import TypeAlias, Type
import warnings

from ..core.interface import TypeCaster
from ..settings import Settings


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
            _set_maybe_warn(hint, _STRICT_CUSTOM_HANDLERS, handler)
    else:
        for hint in type_hints:
            _set_maybe_warn(hint, _CUSTOM_HANDLERS, handler)


def unregister_handler(type_hint: TypeAlias) -> None:
    if type_hint in _STRICT_CUSTOM_HANDLERS:
        del _STRICT_CUSTOM_HANDLERS[type_hint]
    elif type_hint in _CUSTOM_HANDLERS:
        del _CUSTOM_HANDLERS[type_hint]


def _set_maybe_warn(type_hint: TypeAlias, handler_dict: dict[str, type[TypeCaster]], handler: type[TypeCaster]) -> None:
    if type_hint in handler_dict and Settings.WARN_ON_HANDLER_OVERRIDE:
        warnings.warn(f"Handler for '{type_hint}' already exists, will override", UserWarning)
    handler_dict[type_hint] = handler
