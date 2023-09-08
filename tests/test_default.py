import typing
import pytest
from datetime import datetime
from dataclasses import dataclass
from fancy_signatures.core.empty import __EmptyArg__
from fancy_signatures.default import (
    DefaultValue,
    Default,
    DefaultFactory,
    EmptyList,
    EmptyDict,
    EmptySet,
    EmptyTuple,
)


@dataclass
class MyClass:
    value_a: int
    value_b: str


def my_default_factory() -> int:
    return datetime.now().year


class CustomDefault(Default[MyClass]):
    def get(self, value: typing.Any) -> MyClass:
        if isinstance(value, __EmptyArg__):
            return MyClass(1, "a")
        return value


@pytest.mark.parametrize(
    "default_value, expectation",
    [
        pytest.param(EmptySet, set, id="set"),
        pytest.param(EmptyList, list, id="list"),
        pytest.param(EmptyTuple, tuple, id="tuple"),
        pytest.param(EmptyDict, dict, id="dict"),
    ],
)
def test__default_factory_builtin(default_value: typing.Any, expectation: type) -> None:
    assert isinstance(default_value(__EmptyArg__()), expectation)


@pytest.mark.parametrize(
    "default_value, expectation",
    [
        pytest.param(EmptySet, {1, 2}, id="set"),
        pytest.param(EmptyList, [1, 2], id="list"),
        pytest.param(EmptyTuple, (1, 2), id="tuple"),
        pytest.param(EmptyDict, {"a": 1}, id="dict"),
    ],
)
def test__default_factory_builtin_value_given(default_value: typing.Any, expectation: type) -> None:
    assert default_value(expectation) == expectation


@pytest.mark.parametrize(
    "default_value, expectation",
    [
        pytest.param(DefaultValue(3), 3, id="int"),
        pytest.param(DefaultValue(3.2), 3.2, id="float"),
        pytest.param(DefaultValue("test"), "test", id="string"),
    ],
)
def test__default_value_builtin(default_value: typing.Any, expectation: typing.Any) -> None:
    assert default_value(__EmptyArg__()) == expectation


@pytest.mark.parametrize(
    "default_value, expectation",
    [
        pytest.param(DefaultValue(3), 4, id="int"),
        pytest.param(DefaultValue(3.2), 4.2, id="float"),
        pytest.param(DefaultValue("test"), "given_value", id="string"),
    ],
)
def test__default_value_builtin_value_given(default_value: typing.Any, expectation: typing.Any) -> None:
    assert default_value(expectation) == expectation


@pytest.mark.parametrize(
    "given_value, expectation",
    [
        pytest.param(__EmptyArg__(), MyClass(1, "a"), id="No value provided"),
        pytest.param(MyClass(2, "b"), MyClass(2, "b"), id="Value provided"),
    ],
)
def test__default_custom(given_value: typing.Any, expectation: typing.Any) -> None:
    default = CustomDefault()
    assert default(given_value) == expectation


def test__custom_default_factory() -> None:
    cur_year = datetime.now().year

    default: DefaultFactory[int] = DefaultFactory(my_default_factory)

    assert default(__EmptyArg__()) == cur_year
