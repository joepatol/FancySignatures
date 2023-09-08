from __future__ import annotations
from typing import Any

from .interface import TypeCaster, Default, Validator
from .exceptions import ValidationError, ValidationErrorGroup, TypeValidationError, TypeCastError
from .empty import is_empty


class UnTypedArgField:
    def __init__(self, required: bool, default: Default, validators: list[Validator]) -> None:
        self._required = required
        self._validators = validators
        self._default = default

    def to_typed_argfield(self, typecaster: TypeCaster) -> TypedArgField:
        return TypedArgField(self._required, self._default, typecaster, self._validators)


class TypedArgField(UnTypedArgField):
    def __init__(self, required: bool, default: Default, typecaster: TypeCaster, validators: list[Validator]) -> None:
        self._typecaster = typecaster
        super().__init__(required, default, validators)

    def execute(self, name: str, value: Any, lazy: bool, strict: bool) -> Any:
        value_or_default = self._default(value)
        value_is_empty = is_empty(value_or_default)

        if self._required and value_is_empty:
            raise ValueError(f"Parameter '{name} is required and no default was provided")
        elif value_is_empty:
            return value_or_default

        try:
            typecasted_value = self._typecaster(value_or_default, strict)
        except TypeValidationError as e:
            raise ValidationError(f"Type validation failed. message: {e}", name)
        except TypeCastError as e:
            raise ValidationError(f"Couldn't cast to the correct type. message: {e}", name)

        errors: list[ValidationError] = []
        for validator in self._validators:
            try:
                validator(name, typecasted_value)
            except ValidationError as e:
                if lazy:
                    errors.append(e)
                else:
                    raise e

            if errors:
                raise ValidationErrorGroup(f"Errors during validation of '{name}'", errors)

        return typecasted_value
