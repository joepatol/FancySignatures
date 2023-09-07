import typing
import types

from ..core.interface import TypeCaster

from . import generic_alias
from . import union
from . import special_origins


STRICT_CUSTOM_HANDLERS: dict[typing.TypeAlias, typing.Type[TypeCaster]] = {
    bool: special_origins.BooleanTypeCaster,
    str: special_origins.StringTypeCaster,
    typing.Any: special_origins.AnyTypeCaster,
    typing.Annotated: special_origins.AnnotatedTypeCaster,
    typing.Union: union.UnionTypeCaster,
    types.UnionType: union.UnionTypeCaster,
}  # Type should exactly match


CUSTOM_HANDLERS: dict[typing.TypeAlias, typing.Type[TypeCaster]] = {
    list: generic_alias.ListTupleSetTypeCaster,
    tuple: generic_alias.ListTupleSetTypeCaster,
    set: generic_alias.ListTupleSetTypeCaster,
    dict: generic_alias.DictTypeCaster,
}  # Exact match or subclass
