from typing import _alias

from ..core.interface import TypeCaster


def handle_alias_type_hints(type_hint: _alias) -> TypeCaster:
    from .factory import typecaster_factory
    return typecaster_factory(type_hint.__origin__)
