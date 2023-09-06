from typing import Any

from .related import Related

from fancy_signatures.core.types import __EmptyArg__


def _is_empty(val: Any) -> bool:
    return val is None or isinstance(val, __EmptyArg__)


def mutually_exclusive_args(*args: str) -> Related:
    """Validate only one (or none) of the parameters is provided
    None and __EmptyArg__() are considered as not provided.

    Returns:
        Related: Related object
    """

    def _validation_func(**kwargs: str) -> None:
        _no_more_vals = False
        for val in kwargs.values():
            if _no_more_vals and not _is_empty(val):
                raise ValueError("Params are mutually exclusive")
            elif not _is_empty(val):
                _no_more_vals = True

    return Related(_validation_func, *args)


def complementary_args(*args: str) -> Related:
    """Validate all the arguments are given, or no of the arguments is given

    Returns:
        Related: Related object
    """

    def _validation_func(**kwargs: str) -> None:
        is_empty = [_is_empty(v) for v in kwargs.values()]

        if (not all(is_empty)) and any(is_empty):
            raise ValueError("Parameters are complementary, provide all or none.")

    return Related(_validation_func, *args)
