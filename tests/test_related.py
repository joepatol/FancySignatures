import pytest
from typing import ContextManager, Any
from contextlib import nullcontext as does_not_raise

from fancy_signatures.core.exceptions import ValidationError, ValidatorFailed
from fancy_signatures.core.empty import __EmptyArg__
from fancy_signatures.validation.related import Related
from fancy_signatures.validation.related.validators import (
    mutually_exclusive_args,
    complementary_args,
    hierarchical_args,
    # exactly_one,
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
