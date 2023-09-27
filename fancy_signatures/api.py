from __future__ import annotations

from typing import TypeVar, Callable, Any, cast, overload
import inspect

from .validation.related import Related
from .typecasting import typecaster_factory
from .default import DefaultValue
from .core.field import UnTypedArgField, TypedArgField
from .core.interface import Validator, Default
from .exceptions import ValidationErrorGroup, ValidationError
from .core.empty import __EmptyArg__
from .alias import check_alias_collisions, process_aliases


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def argument(
    *,
    validators: list[Validator] | None = None,
    default: Default | None = None,
    required: bool = True,
    alias: str | None = None,
) -> Any:
    """A function argument

    Args:
        validators (list[Validator] | None, optional): Validators to apply to this argument. Defaults to None.
        default (Default | None, optional): Default value for this argument. Defaults to None.
        required (bool, optional): Whether the argument is required, if not it will default to __EmptyArg__().
        Defaults to True.
        alias (str | None, optional): Alias name for the argument (when parsing from e.g. a dict). Defaults to None.

    Returns:
        UnTypedArgField: Container class for processing the field when the decorated function is called.
        Type hint is `Any` to avoid linter issues when using `argument` as default for a typehinted parameter.
        (`a: int = argument()` would fail)
    """
    default = default if default is not None else DefaultValue()
    validators = validators if validators is not None else []
    return UnTypedArgField(required, default=default, validators=validators, alias=alias)


@overload
def validate(
    *, related: list[Related] | None = None, lazy: bool = False, type_strict: bool = False
) -> Callable[[FuncT], FuncT]:
    ...


@overload
def validate(__func: FuncT) -> FuncT:
    ...


def validate(
    __func: FuncT | None = None, *, related: list[Related] | None = None, lazy: bool = False, type_strict: bool = False
) -> Callable[[FuncT], FuncT]:
    """Validate the functions annotated parameters with the provided 'Validators'.

    Args:
        __func (FuncT, optional): The decorated callable
        lazy (bool, optional): Whether to immediately raise `ValidationErrors` once they occur,
        or collect them in a `ValidationErrorGroup`.
        or whether to validate all parameters and raise an ExceptionGroup with the errors found per parameter.
        Defaults to False.
        Related (list[Related], optional): Related validators that apply a validation function on two or more arguments.
        Defaults to None
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
        if isinstance(func, (classmethod, staticmethod)):
            name = type(func).__name__
            raise TypeError(f"The `@{name}` decorator should be applied after `@validate` (put `@{name}` on top)")
        return cast(FuncT, _FunctionWrapper(func, related, lazy, type_strict))

    if __func is None:
        return wrapper
    else:
        return wrapper(__func)


class _FunctionWrapper:
    __slots__ = (
        "_lazy",
        "_wrapped_func",
        "_func_params",
        "_fields",
        "_related",
        "_strict",
        "__name__",
        "__qualname__",
        "__annotations__",
        "__doc__",
        "__dict__",
    )

    def __init__(self, wrapped_func: FuncT, related_validators: list[Related], lazy: bool, type_strict: bool) -> None:
        annotations_dict = wrapped_func.__annotations__
        signature = inspect.signature(wrapped_func)
        _ = annotations_dict.pop("return", Any)
        named_fields: dict[str, TypedArgField] = {}

        prepared_arg: UnTypedArgField
        for name, parameter in signature.parameters.items():
            typecaster = typecaster_factory(type_hint=annotations_dict.get(name, Any))
            if isinstance(parameter.default, UnTypedArgField):
                prepared_arg = parameter.default
            elif parameter.default == inspect._empty:
                prepared_arg = argument()
            else:
                prepared_arg = argument(default=DefaultValue(parameter.default))
            named_fields[name] = prepared_arg.set_type(typecaster)

        check_alias_collisions(list(named_fields.keys()), [arg.alias for arg in named_fields.values()])

        self._lazy = lazy
        self._wrapped_func = wrapped_func
        self._func_params = signature.parameters
        self._fields = named_fields
        self._related = related_validators
        self._strict = type_strict

        # Copying all interesting stuff from the wrapped function (much like functools.wraps)
        self.__name__ = wrapped_func.__name__
        self.__qualname__ = wrapped_func.__qualname__
        self.__annotations__ = wrapped_func.__annotations__
        self.__module__ = wrapped_func.__module__
        self.__doc__ = wrapped_func.__doc__

    def __get__(self, obj: Any, objtype: type[Any] | None = None) -> _FunctionWrapper:
        """Bind the wrapped function and return another _FunctionWrapper wrapping that."""
        if obj is None:
            try:
                # Handle the case where a method is accessed as a class attribute
                return objtype.__getattribute__(objtype, self.__name__)  # type: ignore
            except AttributeError:
                # This will happen the first time the attribute is accessed
                pass

        bound_function = self._wrapped_func.__get__(obj, objtype)
        result = self.__class__(bound_function, self._related, self._lazy, self._strict)
        if self.__name__ is not None:
            if obj is not None:
                setattr(obj, self.__name__, result)
            else:
                setattr(objtype, self.__name__, result)
        return result

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs = process_aliases(
            {name: field.alias for name, field in self._fields.items()},
            kwargs,
        )

        for i, param_name in enumerate(self._func_params):
            if param_name not in kwargs:
                if i < len(args):
                    kwargs[param_name] = args[i]
                else:
                    kwargs[param_name] = __EmptyArg__()

        errors: list[ValidationError | ValidationErrorGroup] = []
        for name, value in kwargs.items():
            try:
                field = self._fields[name]
            except KeyError:
                raise TypeError(f"Unrecognized argument '{name}' for '{self._wrapped_func.__name__}'")

            try:
                kwargs[name] = field.execute(name, value, self._lazy, self._strict)
            except (ValidationError, ValidationErrorGroup) as e:
                if self._lazy:
                    errors.append(e)
                else:
                    raise e

        if errors:
            raise ValidationErrorGroup(f"Parameter validation for {self._wrapped_func.__name__} failed", errors)

        for related_validator in self._related:
            try:
                related_validator(**kwargs)
            except ValidationError as e:
                if self._lazy:
                    errors.append(e)
                else:
                    raise e

        if errors:
            raise ValidationErrorGroup(f"Related parameter validation for {self._wrapped_func.__name__} failed", errors)

        return self._wrapped_func(**kwargs)
