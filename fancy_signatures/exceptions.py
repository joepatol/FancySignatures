from typing import Any


class ValidationError(Exception):
    def __init__(self, message: str, param: str | list[str]) -> None:
        if isinstance(param, list):
            msg = f"Parameters '{param}' are invalid. {message}."
        else:
            msg = f"Parameter '{param}' is invalid. {message}."
        super().__init__(msg)


class TypeCastError(TypeError):
    def __init__(self, expected_type: type | tuple[Any, ...], extra_info: str | None = None) -> None:
        super().__init__(f"Couldn't cast to correct type: {expected_type}. {extra_info if extra_info else ''}")


class UnCastableType(TypeCastError):
    def __init__(self, expected_type: type | tuple[Any, ...]) -> None:
        super().__init__(expected_type, extra_info="It's impossible to a type of: `{expected_type}`")


class ValidatorFailed(ValueError):
    pass


class TypeValidationError(TypeError):
    pass


class ValidationErrorGroup(ExceptionGroup, ValidationError):
    pass
