import pytest
from typing import Any

from fancy_signatures.typecasting.special_origins import (
    AnyTypeCaster,
    # AnnotatedTypeCaster,
    StringTypeCaster,
    # BooleanTypeCaster,
)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(None, "None"),
        pytest.param(1, "1"),
        pytest.param([1, 2], "[1, 2]"),
        pytest.param("a", "a"),
        pytest.param({"a": 1}, "{'a': 1}"),
    ],
)
def test__string_cast(value: Any, expectation: str) -> None:
    c = StringTypeCaster(str)

    assert c.cast(value) == expectation


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(None, False),
        pytest.param(1, False),
        pytest.param([1, 2], False),
        pytest.param("a", True),
        pytest.param({"a": 1}, False),
    ],
)
def test__string_validate(value: Any, expectation: bool) -> None:
    c = StringTypeCaster(str)

    assert c.validate(value) is expectation


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None),
        pytest.param(1),
        pytest.param([1, 2]),
        pytest.param("a"),
        pytest.param({"a": 1}),
    ],
)
def test__any_validate(value: Any) -> None:
    c = AnyTypeCaster(Any)

    assert c.validate(value) is True


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None),
        pytest.param(1),
        pytest.param([1, 2]),
        pytest.param("a"),
        pytest.param({"a": 1}),
    ],
)
def test__any_cast(value: Any) -> None:
    c = AnyTypeCaster(Any)

    assert c.cast(value) == value
