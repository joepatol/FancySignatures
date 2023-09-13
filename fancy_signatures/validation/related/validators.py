from .related import Related
from fancy_signatures.exceptions import ValidatorFailed
from fancy_signatures.core.empty import is_empty


def mutually_exclusive_args(*args: str, allow_none: bool = True) -> Related:
    """Validate only one (or none) of the parameters is provided.
    __EmptyArg__() is considered as not provided.

    Args:
        allow_none (bool, optional): Whether to consider `None` as not provided. Defaults to True.

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(**kwargs: str) -> None:
        _no_more_vals = False
        for val in kwargs.values():
            if allow_none and val is None:
                empty = True
            else:
                empty = is_empty(val)
            if not empty and _no_more_vals:
                raise ValidatorFailed(f"Params '{list(kwargs.keys())}' are mutually exclusive")
            elif not empty:
                _no_more_vals = True

    return Related(_validation_func, *args)


def exactly_x(*args: str, x: int, allow_none: bool = True) -> Related:
    """Validate exactly x of the parameters is provided.
    __EmptyArg__() is considered as not provided.

    Args:
        allow_none (bool, optional): Whether to consider `None` as not provided. Defaults to True.

    Returns:
        Related: _description_
    """

    def _validation_func(**kwargs: str) -> None:
        not_empty_count = 0
        for arg in kwargs.values():
            if allow_none and arg is None:
                empty = True
            else:
                empty = is_empty(arg)
            if not empty:
                not_empty_count += 1

        if not_empty_count != x:
            raise ValidatorFailed(f"Provide exactly one of '{list(kwargs.keys())}'")

    return Related(_validation_func, *args)


def complementary_args(*args: str, allow_none: bool = True) -> Related:
    """Validate all the arguments are given, or no of the arguments is given

    Args:
        allow_none (bool, optional): Whether to consider `None` as not provided. Defaults to True.

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(**kwargs: str) -> None:
        if allow_none:
            args_empty = [is_empty(v) or v is None for v in kwargs.values()]
        else:
            args_empty = [is_empty(v) for v in kwargs.values()]

        if (not all(args_empty)) and any(args_empty):
            raise ValidatorFailed("Parameters are complementary, provide all or none.")

    return Related(_validation_func, *args)


def hierarchical_args(owner: str, slaves: list[str], allow_none: bool = True) -> Related:
    """If the owner arg is provided all slave args should be provided as well

    Args:
        owner (str): Name of the owner argument
        slaves (list[str]): List of names of the slave arguments
        allow_none (bool, optional): Whether to consider `None` as not provided. Defaults to True.

    Returns:
        Related: Related object which can be provided to @validate
    """

    def _validation_func(*, owner_value: str, **slaves: str) -> None:
        if allow_none:
            owner_empty = owner_value is None or is_empty(owner_value)
            any_slave_empty = any([is_empty(slave) or slave is None for slave in slaves.values()])
        else:
            owner_empty = is_empty(owner_value)
            any_slave_empty = any([is_empty(slave) for slave in slaves.values()])

        if any_slave_empty and not owner_empty:
            raise ValidatorFailed(f"If '{owner}' is provided, '{list(slaves.keys())}' should also be provided")

    return Related(_validation_func, *slaves, owner_value=owner)
