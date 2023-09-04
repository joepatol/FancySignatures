from dataclasses import dataclass
import typing
from contextlib import nullcontext as does_not_raise

from pydantic import BaseModel

import pytest
from fancy_signatures.typecasting.factory import typecaster_factory
from fancy_signatures.core.exceptions import TypeValidationError


@dataclass
class _CustomType:
    a: int
    b: str


class _PydanticType(BaseModel):
    a: int
    c: str


@pytest.mark.parametrize(
    "value, context",
    [
        pytest.param(
            {"custom": [_CustomType(1, "b")], "pydantic": [_PydanticType(a=1, c="b")], "builtin": 2.2},
            does_not_raise(),
            id="ok",
        ),
        pytest.param(
            {"custom": [_CustomType(1, "b")], "pydantic": [_PydanticType(a=2, c="b")], "builtin": [1, 2]},
            pytest.raises(TypeValidationError),
            id="fail builtin",
        ),
        pytest.param(
            {"custom": (_CustomType(1, "b")), "pydantic": [_PydanticType(a=2, c="b")], "builtin": 1.2},
            pytest.raises(TypeValidationError),
            id="fail not list",
        ),
    ],
)
def test__strict_complex(value: typing.Any, context: typing.ContextManager):
    caster = typecaster_factory(dict[str, list[_CustomType] | list[_PydanticType] | float])

    with context:
        caster(value, True)


def test__correct_cast_complex() -> None:
    caster = typecaster_factory(dict[str, list[_CustomType] | list[_PydanticType] | float])

    input_value = {"custom": [{"a": 1, "b": "b"}], "pydantic": [{"a": 3, "c": "c"}], "builtin": "1.2"}

    result = caster(input_value, False)
    assert result == {"custom": [_CustomType(a=1, b="b")], "pydantic": [_PydanticType(a=3, c="c")], "builtin": 1.2}


@pytest.mark.parametrize(
    "strict, context",
    [
        pytest.param(True, pytest.raises(TypeValidationError), id="strict"),
        pytest.param(False, does_not_raise(), id="Not strict"),
    ],
)
def test__pydantic(strict: bool, context: typing.ContextManager) -> None:
    caster = typecaster_factory(_PydanticType)

    with context:
        caster({"a": 1, "c": "2"}, strict)


@pytest.mark.parametrize(
    "input_value", [pytest.param(1, id="integer"), pytest.param(2.0, id="float"), pytest.param([1, 2], id="list")]
)
def test__basic_typecast(input_value: typing.Any) -> None:
    caster = typecaster_factory(str)
    r = caster(input_value, False)
    assert isinstance(r, str)


def test__strict_basic_type() -> None:
    caster = typecaster_factory(int)

    with pytest.raises(TypeValidationError):
        caster("10", True)


def test__strict_list_generic_alias() -> None:
    caster = typecaster_factory(list[int])

    with pytest.raises(TypeValidationError):
        caster(("a", "b"), True)

    with pytest.raises(TypeError):
        caster([1, "2"], True)


def test__strict_dict_generic_alias() -> None:
    caster = typecaster_factory(dict[str, float])
    caster({"a": 1.0}, True)

    with pytest.raises(TypeValidationError):
        caster({"a", 1}, True)


def test__strict_union_type() -> None:
    caster = typecaster_factory(int | float)
    caster(1, True)
    caster(2.0, True)

    with pytest.raises(TypeValidationError):
        caster("1", True)


def test__strict_generic_alias_and_union() -> None:
    caster = typecaster_factory(list[str] | tuple[str])
    caster(["A", "B"], True)
    caster(("A", "B"), True)

    with pytest.raises(TypeValidationError):
        caster([1, "B"], True)

    with pytest.raises(TypeValidationError):
        caster((1, 3), True)


def test__strict_custom_type() -> None:
    caster = typecaster_factory(_CustomType)
    caster(_CustomType(1, "a"), True)

    with pytest.raises(TypeValidationError):
        caster({"a": 1, "b": "a"}, True)


def test__strict_generic_alias_with_custom_type() -> None:
    caster = typecaster_factory(list[_CustomType])
    inp = [_CustomType(1, "a"), _CustomType(2, "b")]
    caster(inp, True)

    invalid_inp = [_CustomType(1, "a"), 3]

    with pytest.raises(TypeValidationError):
        caster(invalid_inp, True)


def test__strict_union_generic_alias_custom_type() -> None:
    caster = typecaster_factory(list[_CustomType] | tuple[_CustomType])
    inp = [_CustomType(1, "a"), _CustomType(2, "b")]
    caster(inp, True)

    invalid_inp = (_CustomType(1, "a"), 3)

    with pytest.raises(TypeValidationError):
        caster(invalid_inp, True)


def test__strict_alias() -> None:
    caster = typecaster_factory(typing.List[int])
    caster([1, 2], True)

    with pytest.raises(TypeValidationError):
        caster([1, "2"], True)


@pytest.mark.parametrize(
    "value", [pytest.param(1, id="integer"), pytest.param(2.0, id="float"), pytest.param([1, 2], id="list")]
)
def test__strict_any(value: typing.Any) -> None:
    caster = typecaster_factory(typing.Any)

    with does_not_raise():
        caster(value, True)


@pytest.mark.parametrize(
    "value, output_type",
    [pytest.param(1, int, id="integer"), pytest.param(2.0, float, id="float"), pytest.param([1, 2], list, id="list")],
)
def test___any(value: typing.Any, output_type: type) -> None:
    caster = typecaster_factory(typing.Any)

    result = caster(value, False)
    assert isinstance(result, output_type)


@pytest.mark.parametrize(
    "value, context",
    [
        pytest.param("a", does_not_raise(), id="string"),
        pytest.param(None, does_not_raise(), id="None"),
        pytest.param(1, pytest.raises(TypeValidationError), id="invalid value"),
    ],
)
def test__strict_optional(value: typing.Any, context: typing.ContextManager) -> None:
    caster = typecaster_factory(typing.Optional[str])

    with context:
        caster(value, True)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(3, False, id="integer"),
        pytest.param("3", True, id="string")
    ]
)
def test__annotated_validate(value: typing.Any, expectation: bool) -> None:
    caster = typecaster_factory(typing.Annotated[str, "metadata"])
    
    assert caster.validate(value) == expectation
