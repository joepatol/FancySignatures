import pytest
from typing import Any, Union, List, Tuple

from fancy_signatures.exceptions import TypeCastError
from fancy_signatures.typecasting.union import UnionTypeCaster


@pytest.mark.parametrize("origin", [int | float, Union[int, float]])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, True),
        pytest.param(1.2, True),
        pytest.param("1", False),
        pytest.param([1, 2], False),
    ],
)
def test__union_validate(origin: type, value: Any, expectation: bool) -> None:
    c = UnionTypeCaster(origin)

    assert c.validate(value) is expectation


@pytest.mark.parametrize(
    "origin",
    [
        pytest.param(list[float | int] | tuple[float | int, float | int]),
        pytest.param(Union[List[Union[float, int]], Tuple[Union[float, int], Union[float, int]]]),
    ],
)
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], True),
        pytest.param(1.2, False),
        pytest.param(["1", 2], False),
        pytest.param((1.3, 2), True),
        pytest.param("(1.3,2)", False),
    ],
)
def test__union_validate_generic_origin(origin: type, value: Any, expectation: bool) -> None:
    c = UnionTypeCaster(origin)

    assert c.validate(value) is expectation


@pytest.mark.parametrize("origin", [int | float, Union[float, int]])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, 1),
        pytest.param("1", 1),
        pytest.param("1.2", 1.2),
    ],
)
def test__union_cast(origin: type, value: Any, expectation: bool) -> None:
    c = UnionTypeCaster(origin)

    assert c.cast(value) == expectation


def test__order_matters_for_cast() -> None:
    c = UnionTypeCaster(int | float)

    assert c.cast(1.2) == 1


@pytest.mark.parametrize(
    "origin",
    [
        pytest.param(list[float | int] | tuple[float | int]),
        pytest.param(Union[List[Union[float, int]], Tuple[Union[float, int]]]),
    ],
)
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], [1, 2]),
        pytest.param("(1.2, 1.2)", [1.2, 1.2]),
        pytest.param(["1", 2], [1, 2]),
        pytest.param((1.3, 2), [1.3, 2]),
        pytest.param('[1.3,"2"]', [1.3, 2]),
        pytest.param({1: 2, 3: 4}, [1, 3]),
    ],
)
def test__union_cast_generic_origin(origin: type, value: Any, expectation: bool) -> None:
    origin
    c = UnionTypeCaster(origin)

    assert c.cast(value) == expectation


class NoString:
    def __str__(self) -> str:
        raise TypeError("Cannot cast to string")


@pytest.mark.parametrize(
    "origin, value",
    [
        pytest.param(int | float, [1, 3]),
        pytest.param(list | tuple, "a"),
        pytest.param(list | tuple, 1),
        pytest.param(dict | list, "a"),
        pytest.param(str | int, NoString(), id="Object no string"),
    ],
)
def test__union_cast_fail(origin: type, value: Any) -> None:
    c = UnionTypeCaster(origin)

    with pytest.raises(TypeCastError):
        c.cast(value)
