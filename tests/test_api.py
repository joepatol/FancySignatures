from typing import Any, ContextManager
import pytest
from contextlib import nullcontext as does_not_raise
from fancy_signatures.api import validate, argument
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
    a: int = argument(validators=[PositiveInt, ExBlacklisted], required=False),
    b: list[int] = argument(required=True, default=EmptyList, validators=[MaxInputListLength]),
    c: int = argument(validators=[PositiveInt, ExBlacklisted], required=False),
) -> list[int]:
    if is_empty(a):
        to_append = c
    else:
        to_append = a
    b.append(to_append)
    return b


@validate(lazy=True, related=[exactly_one("a", "c")], type_strict=False)
def func_1_lazy(
    a: int | None = argument(validators=[OptionalPositiveInt, ExBlacklisted], required=False),
    b: list[int] = argument(required=True, default=EmptyList, validators=[MaxInputListLength]),
    c: int | None = argument(validators=[OptionalPositiveInt, ExBlacklisted], required=False),
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
    a: int = argument(default=Zero),
    b: int | None = None,
) -> int:
    if b is None:
        b = 0
    return a + b


@validate(lazy=True, type_strict=True)
def func_2_lazy(
    a: int = argument(default=Zero, validators=[GE(0), MultipleOfValidator(2)]),
    b: int | None = argument(validators=[OptionalLT(10)]),
) -> int:
    if b is None:
        b = 0
    return a + b


@validate
def int_or_float(a: int | float) -> int | float:
    return a


@validate
def alias_func(a: int, b: int = argument(alias="c")) -> int:
    return a + b


class MyClass:
    classvar: str = "classvar"

    def __init__(self, base: int) -> None:
        self._base = base

    @validate(lazy=False)
    def my_method(self, a: int, b: int = argument(validators=[PositiveInt])) -> int:
        return a + b + self._base

    @classmethod
    @validate(lazy=False)
    def my_classmethod(cls, a: str) -> str:
        return f"Got {a}, had {cls.classvar}"

    @staticmethod
    @validate
    def my_staticmethod(a: str) -> str:
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


def test__method_decorated() -> None:
    c = MyClass(1)
    assert c.my_method(1, 2) == 4


def test__classmethod_decorated() -> None:
    assert MyClass.my_classmethod("test") == "Got test, had classvar"


def test__staticmethod_decorated() -> None:
    assert MyClass.my_staticmethod("test") == "test"


def test__classmethod_decorated_invalid() -> None:
    with pytest.raises(TypeError):

        class A:
            @validate
            @classmethod
            def method(cls) -> None:
                return None

        A()


def test__related_parameter_not_in_signature() -> None:
    @validate(related=[exactly_one("a", "b")])
    def func(a: int) -> int:
        return a

    with pytest.raises(TypeError):
        func(a=1)


def test__alias() -> None:
    inp = {
        "a": 1,
        "c": 2,
    }

    assert alias_func(**inp) == 3
    assert alias_func(a=1, c=4) == 5  # type: ignore


def test__aliases_collide_with_param_name() -> None:
    with pytest.raises(ValueError):

        @validate
        def test_func(a: str, b: str = argument(alias="a")) -> str:
            return a + b

        test_func("a", "b")


class Course:
    @validate
    def __init__(self, name: str, cost: float) -> None:
        self._name = name
        self._cost = cost


def test__init_decorated() -> None:
    c = Course(**{"name": "a", "cost": 1.2})  # type: ignore

    assert c._cost == 1.2
