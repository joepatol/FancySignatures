import pytest
from typing import ContextManager, Any
from contextlib import nullcontext as does_not_raise

from fancy_signatures.exceptions import ValidationError, ValidatorFailed
from fancy_signatures.core.empty import __EmptyArg__
from fancy_signatures.validation.related import Related
from fancy_signatures.validation.related.validators import (
    mutually_exclusive_args,
    complementary_args,
    hierarchical_args,
    exactly_x,
    switch_dependent_arguments,
)


def this_bigger_than_that(this: int, that: int) -> None:
    if not this > that:
        raise ValidatorFailed("Left should be bigger than right")


@pytest.mark.parametrize(
    "a, b, expectation",
    [
        pytest.param(1, 2, pytest.raises(ValidationError), id="A bigger than B"),
        pytest.param(2, 2, pytest.raises(ValidationError), id="Equal"),
        pytest.param(2, 1, does_not_raise(), id="B bigger than A"),
    ],
)
def test__related(a: int, b: int, expectation: ContextManager) -> None:
    v = Related(this_bigger_than_that, this="a", that="b")

    with expectation:
        v(a=a, b=b)


@pytest.mark.parametrize(
    "a, b, expectation",
    [
        pytest.param(1, 2, pytest.raises(ValidationError), id="Both given"),
        pytest.param(None, 2, does_not_raise(), id="One None"),
        pytest.param(2, __EmptyArg__(), does_not_raise(), id="One __EmptyArg__"),
        pytest.param(None, __EmptyArg__(), does_not_raise(), id="Both empty"),
    ],
)
def test__mutually_exclusive_args(a: Any, b: Any, expectation: ContextManager) -> None:
    v = mutually_exclusive_args("a", "b")

    with expectation:
        v(a=a, b=b)


@pytest.mark.parametrize(
    "a, b, expectation",
    [
        pytest.param(1, 2, does_not_raise(), id="Both given"),
        pytest.param(None, 2, pytest.raises(ValidationError), id="One None"),
        pytest.param(2, __EmptyArg__(), pytest.raises(ValidationError), id="One __EmptyArg__"),
        pytest.param(None, __EmptyArg__(), does_not_raise(), id="Both empty"),
    ],
)
def test__complementary_args(a: Any, b: Any, expectation: ContextManager) -> None:
    v = complementary_args("a", "b")

    with expectation:
        v(a=a, b=b)


@pytest.mark.parametrize(
    "a, b, c, expectation",
    [
        pytest.param(1, 2, 3, does_not_raise(), id="all provided"),
        pytest.param(1, 2, None, pytest.raises(ValidationError), id="One missing"),
        pytest.param(None, 3, None, does_not_raise(), id="Owner not provided and missing"),
        pytest.param(1, __EmptyArg__(), 3, pytest.raises(ValidationError), id="EmptyArg provided"),
    ],
)
def test__hierarchical_args(a: Any, b: Any, c: Any, expectation: ContextManager) -> None:
    v = hierarchical_args(owner="a", slaves=["b", "c"])

    with expectation:
        v(a=a, b=b, c=c)


@pytest.mark.parametrize(
    "a, b, expectation",
    [
        pytest.param(1, 2, pytest.raises(ValidationError), id="Both given"),
        pytest.param(None, 2, does_not_raise(), id="One None"),
        pytest.param(2, __EmptyArg__(), does_not_raise(), id="One __EmptyArg__"),
        pytest.param(None, __EmptyArg__(), pytest.raises(ValidationError), id="Both empty"),
    ],
)
def test__exactly_one(a: Any, b: Any, expectation: ContextManager) -> None:
    v = exactly_x("a", "b", x=1)

    with expectation:
        v(a=a, b=b)


@pytest.mark.parametrize(
    "a, b, c, x, expectation",
    [
        pytest.param(1, None, None, 1, does_not_raise()),
        pytest.param(1, 3, None, 1, pytest.raises(ValidationError)),
        pytest.param(2, 3, None, 2, does_not_raise()),
        pytest.param(2, None, None, 2, pytest.raises(ValidationError)),
        pytest.param(1, 2, 3, 3, does_not_raise()),
        pytest.param(1, None, None, 3, pytest.raises(ValidationError)),
    ],
)
def test__exactly_x(a: Any, b: Any, c: Any, x: int, expectation: ContextManager) -> None:
    v = exactly_x("a", "b", "c", x=x)

    with expectation:
        v(a=a, b=b, c=c)


def test__dont_allow_none_mutually_exclusive_args() -> None:
    v = mutually_exclusive_args("a", "b", allow_none=False)

    with pytest.raises(ValidationError):
        v(a=1, b=None)


def test__dont_allow_none_exactly_one() -> None:
    v = exactly_x("a", "b", x=1, allow_none=False)

    with pytest.raises(ValidationError):
        v(a=1, b=None)


def test__dont_allow_none_complementary_args() -> None:
    v = complementary_args("a", "b", allow_none=False)

    with does_not_raise():
        v(a=1, b=None)


def test__dont_allow_none_hierarchical_args() -> None:
    v = hierarchical_args(owner="a", slaves=["b"], allow_none=False)

    with does_not_raise():
        v(a=1, b=None)


@pytest.mark.parametrize(
    "switch, val_a, val_b, expectation",
    [
        pytest.param(True, None, 1, pytest.raises(ValidationError)),
        pytest.param(True, 1, 1, does_not_raise()),
        pytest.param(True, __EmptyArg__(), 1, pytest.raises(ValidationError)),
    ],
)
def test__switch_dependent_arguments(switch: Any, val_a: Any, val_b: Any, expectation: ContextManager) -> None:
    v = switch_dependent_arguments("val_a", "val_b", switch_arg="switch")

    with expectation:
        v(val_a=val_a, val_b=val_b, switch=switch)
