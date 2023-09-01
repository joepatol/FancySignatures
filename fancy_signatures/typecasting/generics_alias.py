from typing import Any, get_args, Callable
from types import GenericAlias

from ..core.interface import TypeCaster
from ..core.exceptions import TypeValidationError


GenericAliasTypecasterFunc = Callable[[GenericAlias], TypeCaster]


def handle_generic_alias_hints(type_hint: GenericAlias) -> TypeCaster:
    return GenericAliasTypecaster.build(type_hint)


def _handle_list_or_tuple_generic(origin_hint: GenericAlias) -> TypeCaster:
    next_hint = get_args(origin_hint)[0]
    origin = origin_hint.__origin__
    def _handler_func(value: list[Any], strict: bool) -> list[Any]:
        if strict and not isinstance(value, origin):
            raise TypeValidationError(f"Incorrect type, should be '{origin}'")
        
        from .factory import typecaster_factory
        return origin_hint([typecaster_factory(next_hint)(x, strict) for x in value])
    return TypeCaster(_handler_func)


def _handle_dict_generic(origin_hint: GenericAlias) -> TypeCaster:
    next_hint = get_args(origin_hint)
    key_hint = next_hint[0]
    value_hint = next_hint[1]
    def _handler_func(value: Any, strict: bool) -> dict[Any, Any]:
        if strict and not isinstance(value, dict):
            raise TypeValidationError(f"Incorrect type, should be '{dict}'")
        
        from .factory import typecaster_factory
        return {
            typecaster_factory(key_hint)(k, strict): typecaster_factory(value_hint)(v, strict) 
            for k, v in value.items()
        }
    return TypeCaster(_handler_func)


class GenericAliasTypecaster: 
    _handlers: dict[type, GenericAliasTypecasterFunc] = {
        list: _handle_list_or_tuple_generic,
        dict: _handle_dict_generic,
        tuple: _handle_list_or_tuple_generic,
    }

    @classmethod
    def build(cls, annotation: GenericAlias) -> TypeCaster:
        try:
            handler = cls._handlers[annotation.__origin__]
        except KeyError:
            raise KeyError(
                f"No GenericAlias handler found for {annotation.__origin__}. Consider"
                "adding one by using GenericAliasTypecaster.add_handler"
            )
        return handler(annotation)
    
    @classmethod
    def add_handler(cls, origin: type, handler: GenericAliasTypecasterFunc) -> None:
        cls._handlers[origin] = handler
