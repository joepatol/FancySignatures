from fancy_signatures.api import validate


@validate
def basic_int(a: int) -> int:
    return a


@validate
def basic_str(a: str) -> str:
    return a
