from typing import Any, ContextManager
import pytest
from contextlib import nullcontext as does_not_raise
from fancy_signatures.api import validate, arg
from fancy_signatures.validation.validators import (
    GE,
    BlackListedValues,
    MaxLength,
    OptionalGE,
    MultipleOfValidator,
    OptionalLT,
)
from fancy_signatures.default import DefaultValue, EmptyList
from fancy_signatures.validation.related.validators import exactly_one
from fancy_signatures.exceptions import ValidationError, ValidationErrorGroup
from fancy_signatures.core.empty import __EmptyArg__, is_empty
from .conftest import ExceptionNotRaised


Zero: DefaultValue[int] = DefaultValue(0)
ExBlacklisted: BlackListedValues[int] = BlackListedValues(10, 20)
PositiveInt: GE[int] = GE(0)
MaxInputListLength: MaxLength[list] = MaxLength(20)
OptionalPositiveInt: OptionalGE = OptionalGE(0)


@validate(lazy=False, related=[exactly_one("a", "c")], type_strict=True)
def func_1(
    a: int = arg(validators=[PositiveInt, ExBlacklisted], required=False),
    b: list[int] = arg(required=True, default=EmptyList, validators=[MaxInputListLength]),
    c: int = arg(validators=[PositiveInt, ExBlacklisted], required=False),
) -> list[int]:
    if is_empty(a):
        to_append = c
    else:
        to_append = a
    b.append(to_append)
    return b


@validate(lazy=True, related=[exactly_one("a", "c")], type_strict=False)
def func_1_lazy(
    a: int | None = arg(validators=[OptionalPositiveInt, ExBlacklisted], required=False),
    b: list[int] = arg(required=True, default=EmptyList, validators=[MaxInputListLength]),
    c: int | None = arg(validators=[OptionalPositiveInt, ExBlacklisted], required=False),
) -> list[int]:
    if is_empty(a) or a is None:
        assert c is not None  # allowing None does make dealing with mypy a bit trickier
        to_append = c
    else:
        to_append = a
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


@validate(lazy=True, type_strict=True)
def func_2_lazy(
    a: int = arg(default=Zero, validators=[GE(0), MultipleOfValidator(2)]),
    b: int | None = arg(validators=[OptionalLT(10)]),
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
def test__custom_int_handler(value: Any, expectation: Any, custom_int_handler: bool) -> None:
    assert custom_int_handler is True
    assert int_or_float(value) == expectation


@pytest.mark.parametrize(
    "value, expected_result",
    [
        pytest.param(__EmptyArg__(), True),
        pytest.param(None, False),
        pytest.param([10, 11, 12], False),
    ],
)
def test__is_empty(value: Any, expected_result: bool) -> None:
    assert is_empty(value) is expected_result


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


@pytest.mark.parametrize(
    "value_a, value_b, value_c, expectation",
    [
        pytest.param("1", [1, 2], None, does_not_raise()),
        pytest.param(None, [1, 2], None, pytest.raises(ValidationErrorGroup)),
        pytest.param(1, [1, 2], 2, pytest.raises(ValidationErrorGroup)),
        pytest.param(2, [1], __EmptyArg__(), does_not_raise()),
        pytest.param(2, (1, 3), __EmptyArg__(), does_not_raise()),
        pytest.param(2.0, "[1, 3]", None, does_not_raise(), id="cast"),
        pytest.param(-1, [1, 3], __EmptyArg__(), pytest.raises(ValidationErrorGroup)),
        pytest.param(11, __EmptyArg__(), __EmptyArg__(), does_not_raise()),
        pytest.param(10, __EmptyArg__(), __EmptyArg__(), pytest.raises(ValidationErrorGroup)),
    ],
)
def test__test_func_1_lazy(value_a: Any, value_b: Any, value_c: Any, expectation: ContextManager) -> None:
    with expectation:
        func_1_lazy(value_a, value_b, value_c)


@pytest.mark.parametrize(
    "input_dict",
    [
        pytest.param({"a": "4", "b": "['1' , '2']"}),
        pytest.param({"a": "None", "b": "['1' , '2']", "c": "4"}),
    ],
)
def test__func_1_lazy_dict_input(input_dict: dict[str, Any]) -> None:
    assert func_1_lazy(**input_dict) == [1, 2, 4]


@pytest.mark.parametrize(
    "a, b, nr_of_exc_func, nr_of_exc_a, nr_of_exc_b",
    [
        pytest.param(-1, None, 1, 2, 0, id="1"),
        pytest.param(-1, 11, 2, 2, 1, id="2"),
    ],
)
def test__lazy_error_count_correct(a: Any, b: Any, nr_of_exc_func: int, nr_of_exc_a: int, nr_of_exc_b: int) -> None:
    try:
        func_2_lazy(a=a, b=b)
        raise ExceptionNotRaised()
    except ValidationErrorGroup as e:
        assert len(e.exceptions) == nr_of_exc_func

        if nr_of_exc_func == 1:
            assert len(e.exceptions[0].exceptions) == max(nr_of_exc_a, nr_of_exc_b)
        elif nr_of_exc_func == 2:
            assert len(e.exceptions[0].exceptions) == nr_of_exc_a
            assert len(e.exceptions[1].exceptions) == nr_of_exc_b


def test__lazy_error_count_one_validation_and_typecast_errors() -> None:
    try:
        func_2_lazy(a=1, b="1")  # type: ignore
        raise ExceptionNotRaised()
    except ValidationErrorGroup as e:
        exc_gr = e.exceptions
        assert len(exc_gr) == 2
        assert len(exc_gr[0].exceptions) == 1
        assert isinstance(exc_gr[1], ValidationError)
