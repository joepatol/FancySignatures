import typing
import types

from ..core.interface import TypeCaster

from . import generic_alias
from . import union
from . import special_origins
from . import default


# Type should exactly match
STRICT_CUSTOM_HANDLERS: dict[typing.TypeAlias, typing.Type[TypeCaster]] = {
    bool: special_origins.BooleanTypeCaster,
    str: special_origins.StringTypeCaster,
    typing.Any: special_origins.AnyTypeCaster,
    typing.Annotated: special_origins.AnnotatedTypeCaster,
    typing.Union: union.UnionTypeCaster,
    types.UnionType: union.UnionTypeCaster,
    type(None): special_origins.NoneTypeCaster,
    int: default.IntOrFloatTypeCaster,
    float: default.IntOrFloatTypeCaster,
}


# Exact match, metaclass match or subclass
CUSTOM_HANDLERS: dict[typing.TypeAlias, typing.Type[TypeCaster]] = {
    list: generic_alias.ListTupleSetTypeCaster,
    tuple: generic_alias.ListTupleSetTypeCaster,
    set: generic_alias.ListTupleSetTypeCaster,
    dict: generic_alias.DictTypeCaster,
    typing._ProtocolMeta: special_origins.ProtocolTypecaster,
}
