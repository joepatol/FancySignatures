from typing import TypeVar

from ..core.interface import Validator


T = TypeVar("T")


class AllowOptionalMixin(Validator[T | None]):
    """MixIn to make a validator allow 'None'."""

    def __call__(self, name: str, obj: T | None) -> T | None:
        if obj is None:
            return obj
        return super().__call__(name, obj)
