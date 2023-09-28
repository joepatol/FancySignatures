# FancySignatures
This package provides an extensive, easy to use API to validate input arguments to functions and methods. It uses standard Python type hints to
validate and/or cast to a given type. It also provides a way to perform additional validation on one or more parameters. Also convenience tools are provided
for easily parsing data.

## Basic usage

The most basic use case is to validate provided function arguments against their type hints.

```python
from fancy_signatures import validate

@validate
def some_func(a: int, b: int) -> int:
    return a + b


some_func(1, 2)  # returns 3
some_func("1", 2)  # returns 3
some_func("a", 2)  # raises ValidationError
```

Use the `lazy` parameter to control whether exceptions are raised or collected in an `ExceptionGroup` and raised after all validations are done


```python
from fancy_signatures import validate


@validate(lazy=True)
def some_func(a: int, b: int) -> int:
    return a + b


some_func("a", "b")  # raises ExceptionGroup with both TypeCastErrors
```

By default, `FancySignatures` will attempt to typecast if type validation fails. To turn this behavior off, use the `type_strict` parameter.


```python
from fancy_signatures import validate


@validate(type_strict=True)
def some_func(a: int, b: int) -> int:
    return a + b


some_func("1", 2)  # raises ValidationError
```

## Argument validators

You can perform other validations on arguments using the `argument` function.

```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import GE

@validate
def some_func(a: int = argument(validators=[GE(0)])) -> int:
    return a

some_func(-1)

# Raises: fancy_signatures.exceptions.ValidationError: Parameter 'a' is invalid. Value should be greater than or equal to 0.
```

### Custom Validators

`FancySignatures` provides a number of built-in validators, but you can also create your own.
Just inherit from the provided `Validator` base class and implement the `validate` method.

```python
from fancy_signatures import validate, argument
from fancy_signatures import Validator
from fancy_signatures.exceptions import ValidatorFailed


class DivisibleByTwo(Validator[int | float]):
    def validate(self, obj: int | float) -> int | float:
        if obj % 2 != 0:
            raise ValidatorFailed("Should be divisible by 2")
        return obj


@validate
def custom_validator_func(a: int = argument(validators=[DivisibleByTwo()])) -> int:
    return a


# fancy_signatures.exceptions.ValidationError: Parameter 'a' is invalid. Should be divisible by 2.
```

Validators should raise `ValidatorFailed` if the validation fails, these exceptions will be caught by `FancySignatures`.
If the validation is successfull, the original input value (`obj`) should be returned.

### Validating optional arguments

For validating optional arguments (`Any | None` or `typing.Optional[Any]`) validators are provided for you.
These validators will be skipped (i.e. they return `None`) if it `None` is passed as an argument.

```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import OptionalGE


@validate
def optional_arg(a: int | None = argument(validators=[OptionalGE(0)])) -> int | None:
    return a

```

For creating your own optional validators, use the `AllowOptionalMixin`.

```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import AllowOptionalMixin


class DivisibleByTwo(AllowOptionalMixin, Validator[int | float]):
    def validate(self, obj: int | float) -> int | float:
        if obj % 2 != 0:
            raise ValidatorFailed("Should be divisible by 2")
        return obj

@validate
def optional_arg(a: int | None = argument(validators=[DivisibleByTwo()])) -> int | None:
    return a
```

## Default values

With `FancySignatures` you can provide defaults like you are used to. If you are using `argument` it also takes a parameter `default` that can be used to provide a value from the
built-in `Default` class. If you so desire you can inherit from it and create you own `Default` object by implementing the `get` method. For most use cases though, the built in
`DefaultValue` and `DefaultFactory` should suffice.

```python
from fancy_signatures import validate, argument
from fancy_signatures.default import DefaultValue, DefaultFactory


@validate
def default_value(a: bool = True, b: bool = argument(default=DefaultValue(True))) -> bool:
    return a and b


@validate
def default_factory(a: list = argument(default=DefaultFactory(list))) -> list:
    return a


print(default_value())
print(default_factory())
```

For convenience, some often used defaults are provided for you. For example `Zero` (equivalent to `DefaultValue(0)`) and `EmptyList` (equivalent to `DefaultFactory(list)`).


## More on the `argument` function

Next to functioning as a container for storing defaults and validators, the `argument` function provides other functionality.

### required
The required parameter controls whether an argument is mandatory. By default it is set to `True` but setting it to `False` means it can be ommitted completely.

**Be aware** `FancySignatures` will pass non-required parameters that were not provided to the function as the `__EmptyArg__` object. To deal with this in your functions
the `is_empty` function is provided.

```python
from fancy_signatures import validate, argument, is_empty


@validate
def empty_arguments(a: str = argument(required=False)) -> str | None:
    if is_empty(a):
        return
    return a


print(empty_arguments())
print(empty_arguments("passed"))
```

If you don't use is empty you will see that `a` is actually an instance of `__EmptyArg__`.

```python
from fancy_signatures import validate, argument


@validate
def empty_arguments(a: str = argument(required=False)) -> str | None:
    return a


print(empty_arguments())  # prints: `FancySignaturesEmptyObject`
```

### alias

The alias paramater allows you to provide an alias name for a parameter. It's useful when data is provided to you from a source you can't control (e.g. a http request). It allows you to use the function argument names you want while not being dependent on the naming of the data you receive.

```python
from fancy_signatures import validate, argument


@validate
def func(input_value: str = argument(alias="inpval")) -> str:
    return input_value


print(func(**{"inpval": "hello world"}))
```


## Related validation

In addition to validating individual arguments `FancySignatures` also provides a way to perform validations accross multiple arguments using the `Related` object.

```python
from fancy_signatures import validate
from fancy_signatures.validation.related import Related


def should_be_greater(a, b):
    if a <= b:
        raise ValidatorFailed("a should be greater than b")


@validate(related=[Related(should_be_greater, "a", "b")])
def related(a: int b: int) -> int: 
    return a + b


related(6, 5)  # OK
related(4, 5)  # Raises ValidationError
```

The `Related` object expects the names of the arguments you want to validate as `args` you can also map function argument names and validator argument names using `kwargs`

```python
from fancy_signatures import validate
from fancy_signatures.validation.related import Related


def should_be_greater(a, b):
    if a <= b:
        raise ValidatorFailed("a should be greater than b")


@validate(related=[Related(should_be_greater, a="input_a", b="input_b")])
def related(input_a: int, input_b: int) -> int: 
    return input_a + input_b


related(6, 5)  # OK
related(4, 5)  # ValidationError: Parameters '['input_a', 'input_b']' are invalid. a should be greater than b.
```

### Builtin related validators

`FancySignatures` also provides a number of builtin related validators which can be found in the `fancy_signatures.validation.related` module.

## More on type validating and typecasting
To perform type vaidation and typecasting `FancySignatures` uses the `TypeCaster` interface. Internally, a number of `TypeCaster` objects are implemented for all common type hints. 

To create a `TypeCaster` for a type hint, you can use the `typecaster_factory` function. It takes a type hint and return the `TypeCaster` for that hint. 

**Note** Type hints that consist of other type hints, like `GenericAlias` types and `Union` are recursively checked. E.g. `list[int]` will return a typecaster for `list` and once the `TypeCaster` is called, it will call `typecaster_factory` again to validate the `int` type.

Each `TypeCaster` has a `validate` and `cast` method, to validate the type hint and cast to the given type hint respectively.


```python
from fancy_signatures.typecasting import typecaster_factory

typecaster = typecaster_factory(list[int])

print(typecaster)  # <fancy_signatures.typecasting.generic_alias.ListTupleSetTypeCaster object>

# In this case the typecaster will internally call the typecaster for int.
print(typecaster.validate([1, "2"]))  # False

print(typecaster.validate([1, 2]))  # False

print(typecaster.cast([1, "2"]))  # [1, 2]
```

### How a `TypeCaster` and type are matched
`FancySignatures` internally keeps track of which `TypeCaster` belongs to which type hint. This is done in 2 dictionaries.

1. `STRICT_CUSTOM_HANLDERS` are only invoked if the type hint exactly matches the type hint the `TypeCaster` was created for

2. `CUSTOM_HANDLERS` are invoked in case of an exact match **or** a subclass.

3. If no match is found in both of the aforementioned dictionaries, the `DefaultTypeCaster` is used. Which unpacks lists or dicts and tries to call the given type with the provided parameters.

### Adding a `TypeCaster`

If you define your own class inheriting from `typing.Generic`, `FancySignatures` will be able to handle it. 

```python
from typing import Generic, TypeVar
from fancy_signatures import validate


T = TypeVar("T")


class MyClass(Generic[T]):
    @property
    def param(self) -> T:
        return self._param
    
    def __init__(self, param: T) -> None:
        self._param = param
        

@validate
def custom_generic(a: MyClass[int]) -> int:
    return a.param

print(custom_generic(MyClass(1)))  # 1

# However no guarantees for the Generic subscription can be given. 
print(custom_generic(MyClass("a")))  # "a"
```

To overcome the problem of `FancySignatures` not knowing how to handle your custom `Generic` classes. You can add your own typecaster by registering it with `FancySignatures`


```python
from typing import Any, Generic, TypeVar, get_args
from fancy_signatures import validate, TypeCaster
from fancy_signatures.typecasting import register_typecaster, typecaster_factory


T = TypeVar("T")


class MyClass(Generic[T]):
    @property
    def param(self) -> T:
        return self._param
    
    def __init__(self, param: T) -> None:
        self._param = param


class MyTypeCaster(TypeCaster[MyClass]):
    def __init__(self, type_hint: Any) -> None:
        super().__init__(type_hint)
        self._subtype = get_args(type_hint)[0]
    
    def validate(self, param_value: Any) -> bool:
        if not isinstance(param_value, MyClass):
            return False
        if not isinstance(param_value.param, self._subtype):
            return False
        return True

    def cast(self, param_value: Any) -> MyClass:
        # If its not MyClass, create a new myclass with the param_value
        if not isinstance(param_value, MyClass):
            param_value = MyClass(param_value)
        # Now use the typecaster_factory to create a caster for the subtype
        param_value._param = typecaster_factory(self._subtype).cast(param_value._param)
        return param_value


# strict=True, so an exact match is required. To also use this caster for subclasses use strict=False
register_typecaster(type_hints=[MyClass], handler=MyTypeCaster, strict=True)


@validate
def custom_generic(a: MyClass[int]) -> int:
    return a.param


r = custom_generic(MyClass("1"))
print(r) # 1
print(type(r))  # <class 'int'>

custom_generic(MyClass([1, 3]))  # ValidationError
```

**Be aware** registering a `TypeCaster` that already exists (e.g. one for `float`) is possible and might sometimes even be desirable to add specific functionality. `FancySignatures` will throw a warning when you do this. A function `unregister_typecaster` can be used to remove typecasters. **This will not reinstate the previous caster**, in order to do that, re-register the `TypeCaster`

## Settings
`FancySignatures` provides a settings module which you can use the customize (for now a limited amount) of behavior.

Currently there are 2 settigns:

- `WARN_ON_HANDLER_OVERRIDE`: bool = True -> Whether to raise a warning when a `TypeCaster` is overriden (e.g. registering a caster for `list`)
- `PROTOCOL_HANDLING`: ProtocolHandlingLevel = ProtocolHandlingLevel.ALLOW -> Whether to allow a `typing.Protocol` as type hints. (Can be `WARN` to raise a warning or `DISALLOW` to raise an `Exception`)

```python
from fancy_signatures.settings import set, ProtocolHandlingLevel

# Change a settings
set("PROTOCOL_HANDLING", ProtocolHandlingLevel.WARN)
```

You can use `settings.reset()` to reset all settings to their original values.

You can use `settings.get_typecast_handlers()` to get a dictionairy of all registered `TypeCasters`

## Classes and methods
Decorating methods and classes is possible. Be aware that for classes, internally the `__init__` method will be wrapped.

So:

```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import GE


@validate
class MyClass:
    def __init__(self, a: int = argument(validators=[GE(0)]), b: str = argument(alias="msg")) -> None:
        self.a = a
        self.b = b
```

Is equivalent to:
```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import GE


class MyClass:
    @validate
    def __init__(self, a: int = argument(validators=[GE(0)]), b: str = argument(alias="msg")) -> None:
        self.a = a
        self.b = b

```

You might find it cleare to directly decorate the `__init__` method, up to you!

With `dataclasses`

```python
from dataclasses import dataclass

from fancy_signatures import validate, argument
from fancy_signatures.validation import GE


@validate
@dataclass
class MyClass:
    a: int = argument(validators=[GE(0)])
    b: str = argument(alias="msg")
```

## Exceptions
While internally `FancySignatures` uses a number of different exceptions. When using `@validate` only a `ValidationError` (when `lazy=False`) or `ValidationErrorGroup` (when `lazy=True`) will be raised. This means you only need to catch one exception based on the `lazy` parameter. Additionally, `ValidationErrorGroup` offers a `to_dict()` mthod to convert the `ExceptionGroup` to a dictionairy.

```python
from fancy_signatures import validate, argument
from fancy_signatures.validation import GE
from fancy_signatures.exceptions import ValidationErrorGroup


@validate(lazy=True)
def my_func(
    a: int = argument(validators=[GE(0)]),
    b: int = argument(validators=[GE(0)]),
) -> int:
    return a + b


try:
    my_func(**{"a": -1, "b": "no_int"})
except ValidationErrorGroup as e:
    print(e.to_dict())

"""
Returns:

{
    'Parameter validation for my_func failed (2 sub-exceptions)': [
        {
            "Errors during validation of 'a' (1 sub-exception)": [
                "Parameter 'a' is invalid. Value should be greater than or equal to 0."
            ]
        }, 
        "Parameter 'b' is invalid. Couldn't cast to the correct type. message: Couldn't cast to correct type: <class 'int'>. Couldn't cast to correct type: <class 'int'>. invalid literal for int() with base 10: 'no_int'."
    ]
}
"""
```

## Full example

Below a working example of how to use the library is provided.
Put some errors in the input data (or remove the default for `cost` for example) to see how `FancySignatures` returns errors

```python
from typing import Any
from dataclasses import dataclass

from fancy_signatures import validate, argument
from fancy_signatures.validation.related import switch_dependent_arguments
from fancy_signatures.exceptions import ValidationErrorGroup
from fancy_signatures.validation.validators import GE, LE
from fancy_signatures.default import DefaultValue


@validate(lazy=True, related=[switch_dependent_arguments("cost", switch_arg="in_stock")])
@dataclass
class Course:
    name: str
    cost: float | None = argument()
    in_stock: bool = argument(default=DefaultValue(True))
        

@validate(lazy=True)
@dataclass
class Student:
    name: str
    age: int
    courses: list[Course] = argument(alias="course_ids")


@validate(lazy=True)
@dataclass
class ClassRoom:
    name: str
    capacity: int = argument(validators=[GE(0), LE(50)], default=DefaultValue(10))


@validate(lazy=True)
def load_students(
    budget: float = argument(validators=[GE(0)]), 
    students: list[Student] = argument(alias="student_info_"),
    classrooms: list[ClassRoom] = argument(alias="rooms"),
) -> None:
    print(budget)
    print(students)
    print(classrooms)


input_data = {
    "budget": "125000",
    "rooms": [
        {
            "name": "1A",
            "capacity": "5"
        },
        {
            "name": "1B",
            "capacity": "3"
        },
        {
            "name": "2A",
            "capacity": "10"
        },
    ],
    "student_info_": [
        {
            "name": "Pete",
            "age": 27,
            "courses": [
                {"name": "a", "cost": "1.2"}
            ]
        },
        {
            "name": "Sarah",
            "age": 25,
            "course_ids": [
                {"name": "b", "cost": "11.2"}
            ]
        }
    ]
}


def main() -> None:
    try:
        load_students(**input_data)
    except ValidationErrorGroup as e:
        print(e.to_dict())

if __name__ == "__main__":
    main()

```

