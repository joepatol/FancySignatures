from fancy_signatures.api import validate


@validate
def basic_int(a: int) -> int:
    return a


@validate
def basic_str(a: str) -> str:
    return a


def test__basic_int() -> None:
    basic_int(1)
    basic_int("1")
    basic_int(1.0)
    

def test__basic_str() -> None:
    basic_str("a")
    basic_str(1)
    basic_str(2)
    basic_str("[1, 2, 3]")
