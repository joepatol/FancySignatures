from fancy_signatures import validate, argument
from fancy_signatures.validation import OptionalLT, MultipleOfValidator, GE
from fancy_signatures.default import Zero
from fancy_signatures.exceptions import ValidationErrorGroup

from .conftest import ExceptionNotRaised


@validate(lazy=True, type_strict=True)
def func(
    a: int = argument(default=Zero, validators=[GE(0), MultipleOfValidator(2)]),
    b: int | None = argument(validators=[OptionalLT(10)]),
) -> int:
    if b is None:
        b = 0
    return a + b


def test__to_dict() -> None:
    expected_result = {
        "Parameter validation for func failed (2 sub-exceptions)": [
            {
                "Errors during validation of 'a' (2 sub-exceptions)": [
                    "Parameter 'a' is invalid. Value should be greater than or equal to 0.",
                    "Parameter 'a' is invalid. Parameter should be a multiple of 2.",
                ]
            },
            {
                "Errors during validation of 'b' (1 sub-exception)": [
                    "Parameter 'b' is invalid. Value should be smaller than or equal to 10."
                ]
            },
        ]
    }

    try:
        func(a=-1, b=11)
        raise ExceptionNotRaised()
    except ValidationErrorGroup as e:
        assert e.to_dict() == expected_result


def test__to_dict_with_exception_and_group() -> None:
    expected_result = {
        "Parameter validation for func failed (2 sub-exceptions)": [
            {
                "Errors during validation of 'a' (1 sub-exception)": [
                    "Parameter 'a' is invalid. Parameter should be a multiple of 2."
                ]
            },
            "Parameter 'b' is invalid. Type validation failed. message: Invalid type, should be int | None.",
        ]
    }
    try:
        func(a=1, b="1")  # type: ignore
        raise ExceptionNotRaised()
    except ValidationErrorGroup as e:
        assert e.to_dict() == expected_result
