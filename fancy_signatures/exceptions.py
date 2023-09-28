from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    """Main validation error class"""

    def __init__(self, message: str, param: str | list[str]) -> None:
        if isinstance(param, list):
            msg = f"Parameters '{param}' are invalid. {message}."
        else:
            msg = f"Parameter '{param}' is invalid. {message}."
        super().__init__(msg)


class MissingArgument(Exception):
    pass


class TypeCastError(TypeError):
    """Error raised when typecasting failed"""

    def __init__(self, expected_type: type | tuple[Any, ...], extra_info: str | None = None) -> None:
        super().__init__(f"Couldn't cast to correct type: {expected_type}. {extra_info if extra_info else ''}")


class UnCastableType(TypeCastError):
    """Error raised when typecasting is not possible for a type"""

    def __init__(self, expected_type: type | tuple[Any, ...]) -> None:
        super().__init__(expected_type, extra_info="It's impossible to cast a type of: `{expected_type}`")


class ValidatorFailed(ValueError):
    """Error raised when a validator fails"""

    pass


class TypeValidationError(TypeError):
    """Error raised when type validation fails"""

    pass


class ValidationErrorGroup(ExceptionGroup, ValidationError):
    """Main error group class"""

    def to_dict(self) -> dict[str, Any]:
        return _exception_group_to_dict(self)


def _exception_group_to_dict(exc_group: ValidationErrorGroup) -> dict[str, Any]:
    exc_list: list[str | dict[str, str]] = []
    for exc_or_exc_group in exc_group.exceptions:
        if isinstance(exc_or_exc_group, ValidationErrorGroup):
            exc_list.append(_exception_group_to_dict(exc_or_exc_group))
        else:
            exc_list.append(str(exc_or_exc_group))
    return {str(exc_group): exc_list}
