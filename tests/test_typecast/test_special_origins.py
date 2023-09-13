import pytest
from typing import Any, Annotated, Protocol

from fancy_signatures.exceptions import TypeCastError, UnCastableType
from fancy_signatures.typecasting.special_origins import (
    AnyTypeCaster,
    AnnotatedTypeCaster,
    StringTypeCaster,
    BooleanTypeCaster,
    ProtocolTypecaster,
)


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(None, "None"),
        pytest.param(1, "1"),
        pytest.param([1, 2], "[1, 2]"),
        pytest.param("a", "a"),
        pytest.param({"a": 1}, "{'a': 1}"),
    ],
)
def test__string_cast(value: Any, expectation: str) -> None:
    c = StringTypeCaster(str)

    assert c.cast(value) == expectation


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(None, False),
        pytest.param(1, False),
        pytest.param([1, 2], False),
        pytest.param("a", True),
        pytest.param({"a": 1}, False),
    ],
)
def test__string_validate(value: Any, expectation: bool) -> None:
    c = StringTypeCaster(str)

    assert c.validate(value) is expectation


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None),
        pytest.param(1),
        pytest.param([1, 2]),
        pytest.param("a"),
        pytest.param({"a": 1}),
    ],
)
def test__any_validate(value: Any) -> None:
    c = AnyTypeCaster(Any)

    assert c.validate(value) is True


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None),
        pytest.param(1),
        pytest.param([1, 2]),
        pytest.param("a"),
        pytest.param({"a": 1}),
    ],
)
def test__any_cast(value: Any) -> None:
    c = AnyTypeCaster(Any)

    assert c.cast(value) == value


@pytest.mark.parametrize(
    "origin, value, expectation",
    [
        pytest.param(str, "a", True),
        pytest.param(str, 1, False),
        pytest.param(list[int], [1], True),
        pytest.param(list[int], [1.2], False),
        pytest.param(dict[str, int], [1], False),
        pytest.param(dict[str, int], {"a": 2}, True),
        pytest.param(bool, "true", False),
    ],
)
def test__annotated_validate(origin: Any, value: Any, expectation: bool) -> None:
    v = AnnotatedTypeCaster(Annotated[origin, "metadata"])

    assert v.validate(value) is expectation


@pytest.mark.parametrize(
    "origin, value, expectation",
    [
        pytest.param(str, "a", "a"),
        pytest.param(str, 1, "1"),
        pytest.param(list[int], [1], [1]),
        pytest.param(list[int], [1.2], [1]),
        pytest.param(list[float], (1.2, 1.4), [1.2, 1.4]),
        pytest.param(dict[str, str], {"a": 2}, {"a": "2"}),
        pytest.param(bool, "true", True),
    ],
)
def test__annotated_cast(origin: Any, value: Any, expectation: bool) -> None:
    v = AnnotatedTypeCaster(Annotated[origin, "metadata"])

    assert v.cast(value) == expectation


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, False),
        pytest.param(True, True),
        pytest.param(False, True),
        pytest.param("True", False),
    ],
)
def test__boolean_validate(value: Any, expectation: bool) -> None:
    v = BooleanTypeCaster(bool)

    assert v.validate(value) is expectation


@pytest.mark.parametrize(
    "value, expectation",
    [
        pytest.param(1, True),
        pytest.param(True, True),
        pytest.param(False, False),
        pytest.param("True", True),
        pytest.param(0, False),
        pytest.param("FaLSe", False),
    ],
)
def test__boolean_cast(value: Any, expectation: Any) -> None:
    v = BooleanTypeCaster(bool)

    assert v.cast(value) == expectation


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(10),
        pytest.param("string"),
        pytest.param([2, 3]),
    ],
)
def test__boolean_cast_fail(value: Any) -> None:
    v = BooleanTypeCaster(bool)

    with pytest.raises(TypeCastError):
        v.cast(value)


class MyInterface(Protocol):
    def method(self, a: int) -> str:
        return str(a)


class ImplementationA:
    def method(self, a: int) -> int:
        return a


class ImplementationB:
    def other_method(self, a: int) -> int:
        return a


@pytest.mark.parametrize(
    "implementation, expected",
    [
        pytest.param(ImplementationA(), True),
        pytest.param(ImplementationB(), False),
        pytest.param(1, False),
    ],
)
def test__protocol_caster(implementation: Any, expected: bool) -> None:
    caster = ProtocolTypecaster(MyInterface)

    assert expected == caster.validate(implementation)


def test__protocol_typecast_fail() -> None:
    caster = ProtocolTypecaster(MyInterface)
    with pytest.raises(UnCastableType):
        caster.cast("a")
