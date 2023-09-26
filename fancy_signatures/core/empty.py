from typing import Any


class __EmptyArg__:
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, __EmptyArg__):
            return True
        return False


def is_empty(param: Any) -> bool:
    """Return whether a variable is 'empty'.
    In the context of fancy_signatures this means it's an instance
    of `__EmptyArg__`.

    Args:
        param (Any): The parameter to check

    Returns:
        bool: True if it's empty, else False
    """
    return isinstance(param, __EmptyArg__)
