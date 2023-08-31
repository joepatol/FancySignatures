from typing import Any
from types import GenericAlias, UnionType

from .user_types import handle_user_types
from .union import handle_union_type_hints
from .generics import handle_generic_alias_hints
from ..core.interface import TypeCaster


def typecaster_factory(type_hint: GenericAlias | type) -> TypeCaster:
    if type_hint == Any:
        return TypeCaster(lambda x: x)
    if isinstance(type_hint, GenericAlias):
        return handle_generic_alias_hints(type_hint)
    if isinstance(type_hint, UnionType):
        return handle_union_type_hints(type_hint)
    else:
        return handle_user_types(type_hint)
