from typing import TypeVar, Any, Generic
from abc import ABC, abstractmethod

from ..exceptions import TypeValidationError, ValidationError, ValidatorFailed, TypeCastError


T = TypeVar("T")


class Validator(Generic[T], ABC):
    """Validator for an argument passed to a function or method"""

    @abstractmethod
    def validate(self, obj: T) -> T:  # pragma: no cover
        """Validate an argument

        If the validation fails `fancy_signatures.exceptions.ValidatorFailed` shoud be raised.
        In case of no errors, the input value should be returned

        Args:
            obj (T): The input value

        Returns:
            T: The validated argument itself
        """
        ...

    def __call__(self, name: str, obj: T) -> T:
        """
        Call the validate method and raise `ValidationError` if it failed.

        Args:
            name (str): The name of the validated argument
            obj (T): The input value

        Raises:
            ValidationError: if the validation fails

        Returns:
            _type_: The validated argument
        """

        try:
            return self.validate(obj)
        except ValidatorFailed as e:
            raise ValidationError(str(e), name)


class Default(Generic[T], ABC):
    """Construct a default value for a function or method argument

    Returns:
        _type_: The default or the value provided
    """

    @abstractmethod
    def get(self, value: Any) -> T:  # pragma: no cover
        """Analyze the input value and return the input value itself or the default

        Args:
            value (Any): The input value

        Returns:
            T: _description_
        """
        ...

    def __call__(self, value: Any) -> T:
        return self.get(value)


class TypeCaster(Generic[T], ABC):
    """Object to validate an arguments type and/or cast it to the correct type"""

    def __init__(self, type_hint: Any) -> None:
        self._type_hint = type_hint

    @abstractmethod
    def validate(self, param_value: Any) -> bool:  # pragma: no cover
        """Validate if a given parameter is of the correct type (adheres to the given type hint)

        Args:
            param_value (Any): The actual value

        Returns:
            bool: `True` if the type is correct `False` otherwise.
        """
        ...

    @abstractmethod
    def cast(self, param_value: Any) -> T:  # pragma: no cover
        """Attempt to cast a value to the correct type.
        If the typecast fails, a `fancy_signatures.exceptions.TypeCastError` should be raised

        Args:
            param_value (Any): The current value

        Returns:
            T: typecasted value
        """
        ...

    def __call__(self, param_value: Any, strict: bool) -> T:
        if not self.validate(param_value):
            if strict:
                raise TypeValidationError(f"Invalid type, should be {self._type_hint}")
            else:
                try:
                    return self.cast(param_value)
                except TypeCastError as e:
                    raise TypeCastError(self._type_hint, extra_info=str(e))
        return param_value
