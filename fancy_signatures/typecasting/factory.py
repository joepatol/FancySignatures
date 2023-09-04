from typing import get_origin, TypeAlias, ParamSpec, Annotated

from ..core.interface import TypeCaster
from .origins import OriginsTypeCaster
from .casters import _STRICT_CUSTOM_HANDLERS, _CUSTOM_HANDLERS


def typecaster_factory(type_hint: TypeAlias) -> TypeCaster:
    """Create a TypeCaster for the given type hint

    First; strict handlers are considered (the type_hint exactly matches the type of the handler)
    Secondly; handlers are considered (the type hint is a subclass of the handler type)
    Lastly; a default TypeCaster is used.

    Args:
        type_hint (TypeAlias): the type hint

    Returns:
        TypeCaster: TypeCaster instance that can be used to validate a given parameter and
        attempt to cast it to the correct type.
    """
    raw_origin = get_origin(type_hint)

    origin = raw_origin if raw_origin is not None else type_hint

    if origin in _STRICT_CUSTOM_HANDLERS:
        return _STRICT_CUSTOM_HANDLERS[origin](type_hint)

    # Paramspec fails subbclass check and is not implemented by default (as of now)
    # so if we get here and it's ParamSpec, we can't continue. Hint to user that they can
    # implement support if they require it.
    if isinstance(origin, ParamSpec):
        raise NotImplementedError(
            "Support for 'ParamSpec' is not implemented. Implement it by adding it as a strict handler,"
            "see `fancy_signatures.typecasting.register_handler`."
        )

    for type_for_handler in _CUSTOM_HANDLERS:
        if issubclass(origin, type_for_handler):
            return _CUSTOM_HANDLERS[type_for_handler](type_hint)

    return OriginsTypeCaster(expected_type=origin)
