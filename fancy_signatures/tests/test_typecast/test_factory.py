from dataclasses import dataclass
from typing import Any, List
from contextlib import nullcontext as does_not_raise

import pytest
from fancy_signatures.typecasting.factory import typecaster_factory
from fancy_signatures.core.exceptions import TypeValidationError


@dataclass
class _CustomType:
    a: int
    b: str


@pytest.mark.parametrize(
    "input_value",
    [
        pytest.param(1, id="integer"),
        pytest.param(2.0, id="float"),
        pytest.param([1, 2], id="list")
    ]
)
def test__basic_typecast(input_value: Any) -> None:
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
    caster = typecaster_factory(List[int])
    caster([1, 2], True)
    
    with pytest.raises(TypeValidationError):
        caster([1, "2"], True)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(1, id="integer"),
        pytest.param(2.0, id="float"),
        pytest.param([1, 2], id="list")
    ]
)
def test__strict_any(value: Any) -> None:
    caster = typecaster_factory(Any)
    
    with does_not_raise():
        caster(value, True)


@pytest.mark.parametrize(
    "value, output_type",
    [
        pytest.param(1, int, id="integer"),
        pytest.param(2.0, float, id="float"),
        pytest.param([1, 2], list, id="list")
    ]
)
def test___any(value: Any, output_type: type) -> None:
    caster = typecaster_factory(Any)
    
    result = caster(value, False)
    assert isinstance(result, output_type)
