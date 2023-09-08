from typing import Any

from .related import Related
from fancy_signatures.core.exceptions import ValidatorFailed
from fancy_signatures.core.empty import is_empty


def _is_empty(val: Any) -> bool:
    return val is None or is_empty(val)


def mutually_exclusive_args(*args: str) -> Related:
    """Validate only one (or none) of the parameters is provided.
    None and __EmptyArg__() are considered as not provided.

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(**kwargs: str) -> None:
        _no_more_vals = False
        for val in kwargs.values():
            if _no_more_vals and not _is_empty(val):
                raise ValidatorFailed(f"Params '{list(kwargs.keys())}' are mutually exclusive")
            elif not _is_empty(val):
                _no_more_vals = True

    return Related(_validation_func, *args)


def complementary_args(*args: str) -> Related:
    """Validate all the arguments are given, or no of the arguments is given

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(**kwargs: str) -> None:
        is_empty = [_is_empty(v) for v in kwargs.values()]

        if (not all(is_empty)) and any(is_empty):
            raise ValidatorFailed("Parameters are complementary, provide all or none.")

    return Related(_validation_func, *args)


def hierarchical_args(owner: str, slaves: list[str]) -> Related:
    """If the owner arg is provided all slave args should be provided as well

    Args:
        owner (str): Name of the owner argument
        slaves (list[str]): List of names of the slave arguments

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(*, owner_value: str, **slaves: str) -> None:
        if not _is_empty(owner_value):
            if any([_is_empty(slave) for slave in slaves.values()]):
                raise ValidatorFailed(f"If '{owner}' is provided, '{list(slaves.keys())}' should also be provided")

    return Related(_validation_func, *slaves, owner_value=owner)
