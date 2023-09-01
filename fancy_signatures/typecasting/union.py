from types import UnionType, GenericAlias
from typing import get_args, Any

from ..core.interface import TypeCaster
from ..core.exceptions import TypeValidationError


def handle_union_type_hints(type_hint: UnionType) -> TypeCaster:
    origins = get_args(type_hint)
    def _handler_func(value: Any, strict: bool) -> Any:
        from .factory import typecaster_factory
        for origin in origins:
            # If it's a genericAlias and the origin is the type of the value
            # it's assummed this is the type we want and we call the factory again
            if isinstance(origin, GenericAlias):
                if isinstance(value, origin.__origin__):
                    return typecaster_factory(origin)(value, strict)
            # If it's not a genericAlias, directly check if the type is correct
            elif isinstance(value, origin):
                return value
        if strict:
            # There is no instance check that matches any of the origins, so strict check fails
            raise TypeValidationError(f"Invalid type, should be one of {origins}")
        # If all else fails, try to cast for each of the origins,
        # the first one that doesn't raise an exception will be returned
        for origin in origins:
            try:
                return typecaster_factory(origin)(value, strict)
            except Exception as e:
                pass
        raise TypeError(f"Unable to cast to any of the types {origins}")
    return TypeCaster(_handler_func)
