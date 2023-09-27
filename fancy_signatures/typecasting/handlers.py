import typing
import warnings

from ..core.interface import TypeCaster
from ..settings import Settings


def register_typecaster(type_hints: list[typing.TypeAlias], handler: typing.Type[TypeCaster], strict: bool) -> None:
    """Register a TypeCaster object that handles a set of type hints.

    Args:
        type_hints (list[TypeAlias]): the type hints supported by this handler
        handler (Type[TypeCaster]): the TypeCaster to handle the value
        strict (bool): Whether the caster is invoked only if the type matches exactly (True)
        or if it's also invoked for all subclasses of type_hints
    """
    from .__handler_lib import STRICT_CUSTOM_HANDLERS, CUSTOM_HANDLERS

    handler_dict = STRICT_CUSTOM_HANDLERS if strict else CUSTOM_HANDLERS

    for hint in type_hints:
        _set_maybe_warn(hint, handler_dict, handler)


def unregister_typecaster(type_hint: typing.TypeAlias) -> None:
    from .__handler_lib import CUSTOM_HANDLERS

    if type_hint in CUSTOM_HANDLERS:
        del CUSTOM_HANDLERS[type_hint]


def unregister_strict_typecaster(type_hint: typing.TypeAlias) -> None:
    from .__handler_lib import STRICT_CUSTOM_HANDLERS

    if type_hint in STRICT_CUSTOM_HANDLERS:
        del STRICT_CUSTOM_HANDLERS[type_hint]


def _set_maybe_warn(
    type_hint: typing.TypeAlias, handler_dict: dict[str, type[TypeCaster]], handler: type[TypeCaster]
) -> None:
    if type_hint in handler_dict and Settings.WARN_ON_HANDLER_OVERRIDE:
        warnings.warn(f"Handler for '{type_hint}' already exists, will override", UserWarning)
    handler_dict[type_hint] = handler
