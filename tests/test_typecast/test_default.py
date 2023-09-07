from typing import Any
import pytest
from dataclasses import dataclass
from pydantic import BaseModel

from fancy_signatures.typecasting.default import DefaultTypeCaster
from fancy_signatures.core.exceptions import TypeCastError


class PydanticType(BaseModel):
    value_a: int
    value_b: int


@dataclass
class CustomType:
    value_a: int
    value_b: int


@pytest.mark.parametrize(
    "origin, value, expectation",
    [
        pytest.param(int, 1, True),
        pytest.param(str, 1, False),
        pytest.param(int, "1", False),
        pytest.param(float, 1, False),
        pytest.param(float, 1.5, True),
        pytest.param(CustomType, 1, False),
        pytest.param(CustomType, CustomType(1, 2), True),
    ],
)
def test__default_caster_validate(origin: type, value: Any, expectation: bool) -> None:
    c = DefaultTypeCaster(origin)

    assert c.validate(value) is expectation


@pytest.mark.parametrize(
    "origin, value, expectation",
    [
        pytest.param(int, 1, 1),
        pytest.param(str, 1, "1"),
        pytest.param(int, "1", 1),
        pytest.param(float, 1, 1.0),
        pytest.param(float, 1.5, 1.5),
        pytest.param(CustomType, [1, 2], CustomType(1, 2)),
        pytest.param(CustomType, {"value_a": 1, "value_b": 2}, CustomType(1, 2)),
        pytest.param(PydanticType, {"value_a": 1, "value_b": 2}, PydanticType(value_a=1, value_b=2)),
        pytest.param(PydanticType, {"value_a": 1, "value_b": "2"}, PydanticType(value_a=1, value_b=2)),
    ],
)
def test__default_caster_cast(origin: type, value: Any, expectation: Any) -> None:
    c = DefaultTypeCaster(origin)

    assert c.cast(value) == expectation


def test__cast_pydantic_error() -> None:
    c = DefaultTypeCaster(PydanticType)

    with pytest.raises(TypeCastError):
        c.cast({"value_a": 1, "value_b": "b"})


def test__cast_custom_type_fail() -> None:
    c = DefaultTypeCaster(CustomType)

    with pytest.raises(TypeCastError):
        c.cast([1, 2, 3])


def test__cast_fail() -> None:
    c = DefaultTypeCaster(int)

    with pytest.raises(TypeCastError):
        c.cast("a")
