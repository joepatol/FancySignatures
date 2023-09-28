py -m pip install --index-url https://test.pypi.org/simple/ --no-deps FancySignatures --upgrade

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
TODO

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

## Custom TypeCasters
TODO

## Settings
TODO

## Classes and methods
TODO

## Exceptions
TODO

## Order of operations
TODO 
Is it necessary?

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
