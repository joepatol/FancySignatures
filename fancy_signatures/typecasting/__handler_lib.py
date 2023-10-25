import typing
import types
from collections.abc import Sequence, Mapping

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
    ...: special_origins.AnyTypeCaster,
    typing.Annotated: special_origins.AnnotatedTypeCaster,
    typing.Union: union.UnionTypeCaster,
    types.UnionType: union.UnionTypeCaster,
    type(None): special_origins.NoneTypeCaster,
    None: special_origins.NoneTypeCaster,
    int: default.IntOrFloatTypeCaster,
    float: default.IntOrFloatTypeCaster,
    tuple: generic_alias.TupleTypeCaster,
    set: generic_alias.SequenceTypeCaster,
}


# Exact match, metaclass match or subclass
CUSTOM_HANDLERS: dict[typing.TypeAlias, typing.Type[TypeCaster]] = {
    Sequence: generic_alias.SequenceTypeCaster,
    Mapping: generic_alias.MappingTypeCaster,
    typing._ProtocolMeta: special_origins.ProtocolTypecaster,
}
