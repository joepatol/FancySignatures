from typing import TypeVar, Callable, Any, cast
import functools
import inspect

from .validation.related import Related
from .typecasting import typecaster_factory
from .default import DefaultValue
from .core.field import UnTypedArgField, TypedArgField
from .core.interface import Validator, Default
from .core.exceptions import ValidationErrorGroup
from .core.types import __EmptyArg__


T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def arg(*, validators: list[Validator] | None = None, default: Default | None = None, required: bool = True) -> UnTypedArgField:
    """A function argument

    Args:
        validators (list[Validator] | None, optional): Validators to apply to this argument. Defaults to None.
        default (Default | None, optional): Default value for this argument. Defaults to None.
        required (bool, optional): Whether the argument is required, if not it will default to __EmptyArg__(). Defaults to True.

    Returns:
        UnTypedArgField: Container class for processing the field when the decorated function is called
    """
    default = default if default is not None else DefaultValue()
    validators = validators if validators is not None else []
    return UnTypedArgField(required, default=default, validators=validators)


def validate(__func: FuncT | None = None, *, related: list[Related] | None = None, lazy: bool = False, type_strict: bool = False) -> Callable[[FuncT], FuncT]:
    """Validate the functions annotated parameters with the provided 'Validators'. 

    Args:
        __func (FuncT, optional): The decorated callable
        lazy (bool, optional): Whether to raise an error on the first parameter one occurs,
        or whether to validate all parameters and raise an ExceptionGroup with the errors found per parameter.
        Defaults to False.
        Related (list[Related], optional): Related validators that apply a validation function on two or more arguments. Defaults to None
        type_strict (bool, optional): Whether to raise an error if a typecheck fails, or attempt a typecast first

    Raises:
        ValidationError: error that occurred during validation of parameters
        ValidationErrorGroup: group of validation errors

    Returns:
        Callable[[FuncT], FuncT]: the decorated callable
    """
    if related is None:
        related = []
        
    def wrapper(func: FuncT) -> FuncT:
        return cast(FuncT, functools.update_wrapper(
            wrapper=_FunctionWrapper(func, related, lazy, type_strict),
            wrapped=func
        ))
        
    if __func is None:
        return wrapper
    else:
        return wrapper(__func)


class _FunctionWrapper:
    def __init__(self, wrapped_func: FuncT, related_validators: list[Related], lazy: bool, type_strict: bool) -> None:
        annotations_dict = wrapped_func.__annotations__
        signature = inspect.signature(wrapped_func)
        _ = annotations_dict.pop('return', Any)
        named_fields: dict[str, TypedArgField] = {}
        
        for name, parameter in signature.parameters.items():
            typecaster = typecaster_factory(type_hint=annotations_dict.get(name, Any))
            if isinstance(parameter.default, UnTypedArgField):
                named_fields[name] = parameter.default.to_typed_argfield(typecaster)
            else:
                named_fields[name] = arg().to_typed_argfield(typecaster)
        
        self._lazy = lazy
        self._wrapped_func = wrapped_func
        self._func_params = signature.parameters
        self._fields = named_fields
        self._related = related_validators
        self._strict = type_strict
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for i, param_name in enumerate(self._func_params):
            if param_name not in kwargs:
                if i < len(args):
                    kwargs[param_name] = args[i]
                else:
                    kwargs[param_name] = __EmptyArg__()
        
        errors: list[BaseException] = []
        for name, value in kwargs.items():
            try:
                field = self._fields[name]
            except KeyError:
                raise TypeError(f"Unrecognized argument '{name}' for '{self._wrapped_func.__name__}'")
            
            try:
                kwargs[name] = field.execute(name, value, self._lazy, self._strict)
            except Exception as e:
                if self._lazy: errors.append(e)
                else: raise e
        
        if errors:
            raise ValidationErrorGroup(
                f"Parameter validation for {self._wrapped_func.__name__} failed", 
                errors
            )
            
        for related_validator in self._related:
            try:
                related_validator(**kwargs)
            except Exception as e:
                if self._lazy: errors.append(e)
                else: raise e
                
        if errors:
            raise ValidationErrorGroup(
                f"Related parameter validation for {self._wrapped_func.__name__} failed", 
                errors
            )

        return self._wrapped_func(**kwargs)
