from typing import Any, ContextManager
import pytest
from contextlib import nullcontext as does_not_raise
from fancy_signatures.api import validate, arg
from fancy_signatures.validation.validators import GE, BlackListedValues, MaxLength
from fancy_signatures.default import DefaultValue, EmptyList
from fancy_signatures.validation.related.validators import mutually_exclusive_args
from fancy_signatures.core.exceptions import ValidationError
from fancy_signatures.core.empty import __EmptyArg__


Zero: DefaultValue[int] = DefaultValue(0)
ExBlacklisted: BlackListedValues[int] = BlackListedValues(10, 20)
PositiveInt: GE[int] = GE(0)
MaxInputListLength: MaxLength[list] = MaxLength(20)


@validate(lazy=False, related=[mutually_exclusive_args("a", "c")], type_strict=True)
def func_1(
    a: int = arg(validators=[PositiveInt, ExBlacklisted], required=False),
    b: list[int] = arg(required=True, default=EmptyList, validators=[MaxInputListLength]),
    c: int = arg(validators=[PositiveInt, ExBlacklisted], required=False),
) -> list[int]:
    to_append = a or c
    b.append(to_append)
    return b


@validate
def func_2(
    a: int = arg(default=Zero),
    b: int | None = None,
) -> int:
    if b is None:
        b = 0
    return a + b


@validate
def int_or_float(a: int | float) -> int | float:
    return a


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1.2, 1.2),
        pytest.param(1, 1),
        pytest.param("1.2", 1.2),
        pytest.param("11", 11),
    ],
)
def test_custom_int_handler(value: Any, expectation: Any, custom_int_handler: bool) -> None:
    assert custom_int_handler is True
    assert int_or_float(value) == expectation


@pytest.mark.parametrize(
    "value_a, value_b, value_c, expectation",
    [
        pytest.param("1", [1, 2], None, pytest.raises(ValidationError)),
        pytest.param(1, [1, 2], 2, pytest.raises(ValidationError)),
        pytest.param(2, [1], __EmptyArg__(), does_not_raise()),
        pytest.param(2, (1, 3), __EmptyArg__(), pytest.raises(ValidationError)),
        pytest.param(2, [1, 3], None, pytest.raises(ValidationError)),
        pytest.param(-1, [1, 3], __EmptyArg__(), pytest.raises(ValidationError)),
        pytest.param(11, __EmptyArg__(), __EmptyArg__(), does_not_raise()),
        pytest.param(10, __EmptyArg__(), __EmptyArg__(), pytest.raises(ValidationError)),
    ],
)
def test__test_func_1(value_a: Any, value_b: Any, value_c: Any, expectation: ContextManager) -> None:
    with expectation:
        func_1(value_a, value_b, value_c)
