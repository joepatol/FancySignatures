from __future__ import annotations

from typing import ContextManager, Any
import pytest
from contextlib import nullcontext as does_not_raise

from fancy_signatures.exceptions import ValidatorFailed, ValidationError
from fancy_signatures.validation.validators import (
    LE,
    LT,
    GT,
    GE,
    MinLength,
    MaxLength,
    BlackListedValues,
    RegexValidator,
    DecimalPlacesValidator,
    MultipleOfValidator,
    IsInValidator,
    OptionalGE,
)


class MyObj:
    def __init__(self, a: str) -> None:
        self._a = a

    def __eq__(self: MyObj, other: object) -> bool:
        if not isinstance(other, MyObj):
            return False
        return other._a == self._a


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, does_not_raise(), id="Equal"),
        pytest.param(0, does_not_raise(), id="Less than"),
        pytest.param(2, pytest.raises(ValidatorFailed), id="Greater than"),
        pytest.param("a", pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__le(value: int, expectation: ContextManager) -> None:
    v: LE = LE(1)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, pytest.raises(ValidatorFailed), id="Equal"),
        pytest.param(0, does_not_raise(), id="Less than"),
        pytest.param(2, pytest.raises(ValidatorFailed), id="Greater than"),
        pytest.param("a", pytest.raises(TypeError), id="Invalid input type"),
        pytest.param("a", pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__lt(value: int, expectation: ContextManager) -> None:
    v: LT = LT(1)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, pytest.raises(ValidatorFailed), id="Equal"),
        pytest.param(0, pytest.raises(ValidatorFailed), id="Less than"),
        pytest.param(2, does_not_raise(), id="Greater than"),
        pytest.param("a", pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__gt(value: int, expectation: ContextManager) -> None:
    v: GT = GT(1)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, does_not_raise(), id="Equal"),
        pytest.param(0, pytest.raises(ValidatorFailed), id="Less than"),
        pytest.param(2, does_not_raise(), id="Greater than"),
        pytest.param("a", pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__ge(value: int, expectation: ContextManager) -> None:
    v: GE = GE(1)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abcd", does_not_raise(), id="String ok"),
        pytest.param("ab", pytest.raises(ValidatorFailed), id="String too short"),
        pytest.param([1, 2, 3, 4], does_not_raise(), id="List ok"),
        pytest.param((1, 2), pytest.raises(ValidatorFailed), id="Tuple too short"),
        pytest.param([1, 2], pytest.raises(ValidatorFailed), id="List too short"),
        pytest.param(1, pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__min_length(value: str | list | tuple, expectation: ContextManager) -> None:
    v: MinLength = MinLength(3)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abc", does_not_raise(), id="String ok"),
        pytest.param("abaa", pytest.raises(ValidatorFailed), id="String too long"),
        pytest.param([1, 2], does_not_raise(), id="List ok"),
        pytest.param((1, 2, 3, 4), pytest.raises(ValidatorFailed), id="Tuple too long"),
        pytest.param([1, 2, "a", "b"], pytest.raises(ValidatorFailed), id="List too long"),
        pytest.param(1, pytest.raises(TypeError), id="Invalid input type"),
    ],
)
def test__max_length(value: str | list | tuple, expectation: ContextManager) -> None:
    v: MaxLength = MaxLength(3)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("abc", does_not_raise(), id="String ok"),
        pytest.param("a", pytest.raises(ValidatorFailed), id="Blacklisted string"),
        pytest.param([1, 2], does_not_raise(), id="List ok"),
        pytest.param([1, "a"], pytest.raises(ValidatorFailed), id="Blacklisted list"),
        pytest.param(1, pytest.raises(ValidatorFailed), id="Blacklisted int"),
    ],
)
def test__blacklisted_values(value: Any, expectation: ContextManager) -> None:
    v = BlackListedValues(1, "a", [1, "a"])

    with expectation:
        v.validate(value)


def test__blacklisted_value_custom_obj() -> None:
    v = BlackListedValues(MyObj("a"))

    with pytest.raises(ValidatorFailed):
        v.validate(MyObj("a"))


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1.22, does_not_raise()),
        pytest.param(1.222, does_not_raise()),
        pytest.param(1.2222, pytest.raises(ValidatorFailed)),
        pytest.param("a", pytest.raises(TypeError)),
        pytest.param(1, does_not_raise()),
    ],
)
def test__decimal_places_validator(value: float, expectation: ContextManager) -> None:
    v = DecimalPlacesValidator(3)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("Ok", does_not_raise()),
        pytest.param("not ok", pytest.raises(ValidatorFailed)),
        pytest.param(12, pytest.raises(TypeError)),
    ],
)
def test__regex_validator(value: str, expectation: ContextManager) -> None:
    v = RegexValidator("[A-Z][a-z]*")

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(4, does_not_raise()),
        pytest.param(1, pytest.raises(ValidatorFailed)),
        pytest.param(2417, pytest.raises(ValidatorFailed)),
        pytest.param("a", pytest.raises(TypeError)),
    ],
)
def test__multipleof_validator(value: int, expectation: ContextManager) -> None:
    v = MultipleOfValidator(2)

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, does_not_raise()),
        pytest.param(4, pytest.raises(ValidatorFailed)),
        pytest.param("b", pytest.raises(ValidatorFailed)),
        pytest.param("a", does_not_raise()),
        pytest.param([1, 2], pytest.raises(ValidatorFailed)),
        pytest.param(MyObj("valid"), does_not_raise()),
        pytest.param(MyObj("invalid"), pytest.raises(ValidatorFailed)),
        pytest.param({"a": 1}, does_not_raise()),
        pytest.param({"a": 2}, pytest.raises(ValidatorFailed)),
    ],
)
def test__isin_validator(value: Any, expectation: ContextManager) -> None:
    v = IsInValidator(1, "a", {"a": 1}, MyObj("valid"))

    with expectation:
        v.validate(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(10, does_not_raise(), id="equal"),
        pytest.param(None, does_not_raise(), id="none"),
        pytest.param(4, pytest.raises(ValidationError), id="smaller"),
    ],
)
def test__optional_validators(value: Any, expectation: ContextManager) -> None:
    v: OptionalGE = OptionalGE(10)

    with expectation:
        v("test", value)
