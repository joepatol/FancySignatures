import pytest
import typing
from fancy_signatures.typecasting.generic_alias import ListTupleSetTypeCaster, DictTypeCaster
from fancy_signatures.core.exceptions import TypeCastError


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


@pytest.mark.parametrize("origin", [list, typing.List])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], [1, 2], id="list to list"),
        pytest.param("[1, 2]", [1, 2], id="string to list"),
        pytest.param("['[1, 2], {1: 3}']", ["[1, 2], {1: 3}"], id="nested"),
        pytest.param((1, 2), [1, 2], id="tuple to list"),
        pytest.param({1, 2}, [1, 2], id="set to list"),
    ],
)
def test__list_caster_cast(origin: type, value: list | tuple | set, expectation: list | tuple | set) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.cast(value) == expectation


@pytest.mark.parametrize("origin", [tuple, typing.Tuple])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param([1, 2], (1, 2), id="list to tuple"),
        pytest.param('[1, "a"]', (1, "a"), id="string list to tuple"),
        pytest.param("(1, 2)", (1, 2), id="string to tuple"),
        pytest.param([[1, 2], {"a": 3}], ([1, 2], {"a": 3}), id="nested"),
        pytest.param({1, 2}, (1, 2), id="set to tuple"),
    ],
)
def test__tuple_caster_cast(origin: type, value: list | tuple | set, expectation: bool) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.cast(value) == expectation


@pytest.mark.parametrize("origin", [set, typing.Set])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("{1, 2}", {1, 2}, id="string to set"),
        pytest.param('{(1, None), "(3, 4)"}', {(1, None), "(3, 4)"}, id="nested"),
        pytest.param((1, 2), {1, 2}, id="tuple to set"),
    ],
)
def test__set_caster_cast(origin: type, value: list | tuple | set, expectation: bool) -> None:
    caster = ListTupleSetTypeCaster(origin)

    assert caster.cast(value) == expectation


@pytest.mark.parametrize("origin", [dict, typing.Dict, typing.DefaultDict, typing.TypedDict])
@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param("{1: 2}", {1: 2}, id="string to dict"),
        pytest.param({"a": 1}, {"a": 1}, id="dict to dict"),
        pytest.param("{1: '[3.0, 4.1]', 2: [2, 4]}", {1: "[3.0, 4.1]", 2: [2, 4]}, id="nested"),
    ],
)
def test__dict_caster_cast(origin: type, value: dict, expectation: bool) -> None:
    caster = DictTypeCaster(origin)

    assert caster.cast(value) == expectation


@pytest.mark.parametrize(
    "origin, value",
    [
        pytest.param(typing.List, 1),
        pytest.param(typing.List, 2.0),
        pytest.param(list, 1),
        pytest.param(tuple, "1"),
    ],
)
def test__list_tuple_set_cast_fail(origin: type, value: typing.Any) -> None:
    caster = ListTupleSetTypeCaster(origin)

    with pytest.raises(TypeCastError):
        caster.cast(value)
