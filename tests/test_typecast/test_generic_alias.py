import pytest
import typing
from fancy_signatures.typecasting.generic_alias import ListTupleSetTypeCaster, DictTypeCaster


@pytest.mark.parametrize("origin", [list, typing.List])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], True),
        pytest.param([1, "a"], True),
        pytest.param("[1, 2]", False),
        pytest.param([[1, 2], {"a": 3}], True),
        pytest.param((1, 2), False),
    ],
)
def test__list_caster_validate(origin: type, value: list | tuple | set, expectation: bool) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.validate(value) is expectation


@pytest.mark.parametrize("origin", [tuple, typing.Tuple])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], False),
        pytest.param([1, "a"], False),
        pytest.param("(1, 2)", False),
        pytest.param(([1, 2], {"a": 3}), True),
        pytest.param((1, 2), True),
    ],
)
def test__tuple_caster_validate(origin: type, value: list | tuple | set, expectation: bool) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.validate(value) is expectation


@pytest.mark.parametrize("origin", [set, typing.Set])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param({1, 2}, True),
        pytest.param({"a": 1}, False),
        pytest.param("{1, 2}", False),
        pytest.param((1, 2), False),
    ],
)
def test__set_caster_validate(origin: type, value: list | tuple | set, expectation: bool) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.validate(value) is expectation


@pytest.mark.parametrize("origin", [dict, typing.Dict, typing.DefaultDict, typing.TypedDict])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param({1, 2}, False),
        pytest.param({"a": 1}, True),
        pytest.param("{1: 2}", False),
        pytest.param((1, 2), False),
    ],
)
def test__dict_caster_validate(origin: type, value: dict, expectation: bool) -> None:
    caster = DictTypeCaster(origin)

    assert caster.validate(value) == expectation
