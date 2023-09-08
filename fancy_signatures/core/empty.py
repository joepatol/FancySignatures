from typing import Any


class __EmptyArg__:
    pass


def is_empty(param: Any) -> bool:
    """Return whether a variable is 'empty'
    In the context of fancy_signatures this means it's an instance
    of __EmptyArg__.

    Args:
        param (Any): The parameter to check

    Returns:
        bool: True if it's empty, else False
    """
    return isinstance(param, __EmptyArg__)
