import pytest
from contextlib import nullcontext as does_not_raise
from typing import Any, ContextManager
from fancy_signatures import Validator, TypeCaster
from fancy_signatures.core.field import TypedArgField, UnTypedArgField
from fancy_signatures.typecasting.factory import typecaster_factory
from fancy_signatures.default import DefaultValue, Default, DefaultFactory, EmptyList
from fancy_signatures.core.empty import __EmptyArg__
from fancy_signatures.exceptions import ValidationErrorGroup, ValidationError, MissingArgument
from fancy_signatures.validation.validators import GT, MultipleOfValidator
from .conftest import ExceptionNotRaised


def test__required_and_no_default_raises() -> None:
    field = TypedArgField(
        required=True,
        typecaster=typecaster_factory(int),
        validators=[],
        default=DefaultValue(),
    )

    with pytest.raises(MissingArgument):
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


@pytest.mark.parametrize(
    "field",
    [
        pytest.param(
            UnTypedArgField(required=True, default=DefaultValue(), validators=[]),
            id="UnTypedArgField",
        ),
        pytest.param(
            TypedArgField(required=True, default=DefaultValue(), validators=[], typecaster=typecaster_factory(str)),
            id="TypedArgField",
        ),
    ],
)
def test__argfield_set_type(field: UnTypedArgField) -> None:
    typed_field = field.set_type(typecaster_factory(int))

    assert isinstance(typed_field, TypedArgField)
    assert typed_field._typecaster._type_hint == int


@pytest.mark.parametrize(
    "validators, nr_of_exc",
    [
        pytest.param([GT(5), MultipleOfValidator(2)], 2),
        pytest.param([GT(5), MultipleOfValidator(1)], 1),
        pytest.param([GT(0), MultipleOfValidator(2)], 1),
    ],
)
def test__field_validators_lazy(validators: list[Validator], nr_of_exc: int) -> None:
    field = TypedArgField(
        required=True,
        default=DefaultValue(),
        typecaster=typecaster_factory(int),
        validators=validators,
    )

    try:
        field.execute("test", 3, lazy=True, strict=False)
        raise ExceptionNotRaised()
    except ValidationErrorGroup as e:
        assert len(e.exceptions) == nr_of_exc


def test__field_validators() -> None:
    field = TypedArgField(
        required=True,
        default=DefaultValue(),
        typecaster=typecaster_factory(int),
        validators=[GT(5), MultipleOfValidator(2)],
    )

    with pytest.raises(ValidationError):
        field.execute("test", 3, lazy=True, strict=False)


@pytest.mark.parametrize(
    "typecaster, expectation",
    [
        pytest.param(typecaster_factory(str), pytest.raises(ValidationError)),
        pytest.param(typecaster_factory(int), does_not_raise()),
        pytest.param(typecaster_factory(float), pytest.raises(ValidationError)),
    ],
)
def test__field_type_strict(typecaster: TypeCaster, expectation: ContextManager) -> None:
    field = TypedArgField(
        required=True,
        default=DefaultValue(),
        typecaster=typecaster,
        validators=[],
    )

    with expectation:
        field.execute("test", 10, lazy=False, strict=True)


@pytest.mark.parametrize(
    "typecaster, expectation",
    [
        pytest.param(typecaster_factory(str), does_not_raise()),
        pytest.param(typecaster_factory(int), does_not_raise()),
        pytest.param(typecaster_factory(list), pytest.raises(ValidationError)),
    ],
)
def test__field_type_not_strict(typecaster: TypeCaster, expectation: ContextManager) -> None:
    field = TypedArgField(
        required=True,
        default=DefaultValue(),
        typecaster=typecaster,
        validators=[],
    )

    with expectation:
        field.execute("test", 10, lazy=False, strict=False)
