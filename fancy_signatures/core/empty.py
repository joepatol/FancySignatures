from typing import Any


class __EmptyArg__:
    pass


def is_empty(param: Any) -> bool:
    return isinstance(param, __EmptyArg__)
