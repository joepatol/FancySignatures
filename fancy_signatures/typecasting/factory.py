from typing import Any, TypeAlias
from types import GenericAlias, UnionType

from .other_types import handle_other_types
from .union import handle_union_type_hints
from .generics_alias import handle_generic_alias_hints
from ..core.interface import TypeCaster


def typecaster_factory(type_hint: TypeAlias) -> TypeCaster:
    if type_hint == Any:
        return TypeCaster(lambda x, _: x)
    elif isinstance(type_hint, GenericAlias):
        return handle_generic_alias_hints(type_hint)
    elif isinstance(type_hint, UnionType):
        return handle_union_type_hints(type_hint)
    else:
        return handle_other_types(type_hint)
