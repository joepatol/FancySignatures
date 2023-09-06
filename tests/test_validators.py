from __future__ import annotations

from typing import ContextManager, Any
import pytest
from contextlib import nullcontext as does_not_raise

from fancy_signatures.core.exceptions import ValidationError
from fancy_signatures.validation.validators import (
    LE,
    LT,
    GT,
    GE,
    MinLength,
    MaxLength,
    BlackListedValues,
)


class MyObj:
    def __init__(self, a: str) -> None:
        self._a = a

    def __eq__(self: MyObj, other: object) -> bool:
        if not isinstance(other, MyObj):
            raise NotImplementedError()
        return other._a == self._a


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, does_not_raise(), id="Equal"),
        pytest.param(0, does_not_raise(), id="Less than"),
        pytest.param(2, pytest.raises(ValidationError), id="Greater than"),
    ],
)
def test__le(value: int, expectation: ContextManager) -> None:
    v: LE = LE(1)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, pytest.raises(ValidationError), id="Equal"),
        pytest.param(0, does_not_raise(), id="Less than"),
        pytest.param(2, pytest.raises(ValidationError), id="Greater than"),
    ],
)
def test__lt(value: int, expectation: ContextManager) -> None:
    v: LT = LT(1)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, pytest.raises(ValidationError), id="Equal"),
        pytest.param(0, pytest.raises(ValidationError), id="Less than"),
        pytest.param(2, does_not_raise(), id="Greater than"),
    ],
)
def test__gt(value: int, expectation: ContextManager) -> None:
    v: GT = GT(1)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, does_not_raise(), id="Equal"),
        pytest.param(0, pytest.raises(ValidationError), id="Less than"),
        pytest.param(2, does_not_raise(), id="Greater than"),
    ],
)
def test__ge(value: int, expectation: ContextManager) -> None:
    v: GE = GE(1)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abcd", does_not_raise(), id="String ok"),
        pytest.param("ab", pytest.raises(ValidationError), id="String too short"),
        pytest.param([1, 2, 3, 4], does_not_raise(), id="List ok"),
        pytest.param((1, 2), pytest.raises(ValidationError), id="Tuple too short"),
        pytest.param([1, 2], pytest.raises(ValidationError), id="List too short"),
    ],
)
def test__min_length(value: str | list | tuple, expectation: ContextManager) -> None:
    v = MinLength(3)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abc", does_not_raise(), id="String ok"),
        pytest.param("abaa", pytest.raises(ValidationError), id="String too long"),
        pytest.param([1, 2], does_not_raise(), id="List ok"),
        pytest.param((1, 2, 3, 4), pytest.raises(ValidationError), id="Tuple too long"),
        pytest.param([1, 2, "a", "b"], pytest.raises(ValidationError), id="List too long"),
    ],
)
def test__max_length(value: str | list | tuple, expectation: ContextManager) -> None:
    v = MaxLength(3)

    with expectation:
        v("test", value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abc", does_not_raise(), id="String ok"),
        pytest.param("a", pytest.raises(ValueError), id="Blacklisted string"),
        pytest.param([1, 2], does_not_raise(), id="List ok"),
        pytest.param([1, "a"], pytest.raises(ValueError), id="Blacklisted list"),
        pytest.param(1, pytest.raises(ValueError), id="Blacklisted int"),
    ],
)
def test__blacklisted_values(value: Any, expectation: ContextManager) -> None:
    v = BlackListedValues(1, "a", [1, "a"])

    with expectation:
        v("test", value)


def test__blacklisted_value_custom_obj() -> None:
    v = BlackListedValues(MyObj("a"))

    with pytest.raises(ValueError):
        v("test", MyObj("a"))
