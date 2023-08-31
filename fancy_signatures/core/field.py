from __future__ import annotations
from typing import Any

from .interface import TypeCaster, Default, Validator
from .exceptions import TypeCastError, ValidationErrorGroup
from .types import __EmptyArg__


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

    def execute(self, name: str, value: Any, lazy: bool) -> Any:
        value_or_default = self._default(value)
        
        if self._required and isinstance(value_or_default, __EmptyArg__):
            raise ValueError(f"Parameter '{name} is required and no default was provided")
        
        try:
            typecasted_value = self._typecaster(value_or_default)
        except Exception as e:
            raise TypeCastError(f"Couldn't cast to correct type. Message: {e}", name)
        
        for validator in self._validators:
            errors: list[BaseException] = []
            try:
                validator(name, typecasted_value)
            except Exception as e:
                if lazy: errors.append(e)
                else: raise e
        
            if errors:
                raise ValidationErrorGroup(f"Errors during validation of '{name}'", errors)
        
        return typecasted_value
