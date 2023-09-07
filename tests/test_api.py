from typing import Any
import pytest
from fancy_signatures.api import validate, arg
from fancy_signatures.validation.validators import GE, BlackListedValues, MaxLength
from fancy_signatures.default import DefaultValue, ListDefault
from fancy_signatures.validation.related.validators import mutually_exclusive_args


ZeroDefault: DefaultValue[int] = DefaultValue(0)
ExBlacklisted: BlackListedValues[int] = BlackListedValues(10, 20)
PositiveInt: GE[int] = GE(0)
MaxInputListLength: MaxLength[list] = MaxLength(20)


@validate(lazy=True, related=[mutually_exclusive_args("a", "c")])
def example_func(
    a: int = arg(validators=[PositiveInt, ExBlacklisted], default=ZeroDefault, required=False),
    b: list[int] = arg(required=True, default=ListDefault, validators=[MaxInputListLength]),
    c: int = arg(validators=[PositiveInt, ExBlacklisted], default=ZeroDefault, required=False),
) -> list[int]:
    to_append = a or c
    b.append(to_append)
    return b


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
