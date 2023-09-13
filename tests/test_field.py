import pytest
from typing import Any
from fancy_signatures.core.field import TypedArgField, UnTypedArgField  # noqa
from fancy_signatures.typecasting.factory import typecaster_factory
from fancy_signatures.default import DefaultValue, Default, DefaultFactory, EmptyList
from fancy_signatures.core.empty import __EmptyArg__


def test__required_and_no_default_raises() -> None:
    field = TypedArgField(
        required=True,
        typecaster=typecaster_factory(int),
        validators=[],
        default=DefaultValue(),
    )

    with pytest.raises(ValueError):
        field.execute("test-field", __EmptyArg__(), False, False)


@pytest.mark.parametrize(
    "input_value, default, expected",
    [
        pytest.param(__EmptyArg__(), DefaultValue(0), 0),
        pytest.param(__EmptyArg__(), DefaultValue(), __EmptyArg__()),
        pytest.param(10, DefaultValue(), 10),
        pytest.param(10, DefaultValue(0), 10),
        pytest.param(None, DefaultValue(0), None),
        pytest.param(__EmptyArg__(), DefaultFactory(list), []),
        pytest.param(__EmptyArg__(), EmptyList, []),
    ],
)
def test__not_required_default_value(input_value: Any, default: Default, expected: Any) -> None:
    field = TypedArgField(
        required=False,
        default=default,
        validators=[],
        typecaster=typecaster_factory(int | list | None),
    )

    result = field.execute(name="test_field", value=input_value, lazy=False, strict=True)
    assert result == expected
