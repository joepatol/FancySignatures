# FancySignatures
This package aims to leverage Python type hints, to validate function and method parameters using a simple decorator.
It also add validation functionality by injecting fields as default values.

## Basic usage

```python
from fancy_signatures import validate

@validate
def some_func(a: int, b: int) -> int:
    return a + b


some_func(1, 2)  # return 3
some_func("1", 2)  # returns 3
some_func("a", 2)  # raises TypeCastError
```

Use the `lazy` parameter to control whether exceptions are raised or collected in an `ExceptionGroup` and raised after all validations are done


```python
from fancy_signatures import validate


@validate(lazy=True)
def some_func(a: int, b: int) -> int:
    return a + b


some_func("a", "b")  # raises ExceptionGroup with both TypeCastErrors
```


On a high level, there are 3 main steps performed:

1. Validate the type hints against the provided parameters, if they don't match attempt to typecast
2. Run all provided validation functions
3. Run all provided `Related` validation functions; validators that use a number of function arguments


If `lazy=True` an `ExceptionGroup` will be raised if an error is found in one of the steps.
For example, if the type validation failed in step 1 an exception will be raised. The next steps will **not** be performed.



## More advanced usage
Next to validating type hints, the package provides a way to apply validations on your parameters using the `arg` function.

```python
from fancy_signatures import validate, arg
from fancy_signatures.validation import IntMin


@validate
def some_func(
    a: int = arg(validators=[IntMin(0)]), 
    b: int = arg(validators=[IntMin(0)]),
) -> int: 
    return a + b


some_func(0, 3)  # Returns 3
some_func(-1, 3)  # Raise ValidationError
```

It's also possible to provide default values. It enables omitted args and kwargs completely.

```python
from fancy_signatures import validate, arg
from fancy_signatures.default import IntDefault


@validate
def some_func(
    a: int, 
    b: int = arg(default=IntDefault(5)),
) -> int: 
    return a + b


some_func(0, 3)  # Returns 3
some_func(2)  # Returns 7
some_func(b=3)  # Raises ValidationError
some_func(a=1)  # Returns 6
```


By default, arguments are required but it can be customized by the `required` parameters.
If you don't provide a default and the parameter is not passed. It will interally be an instance of `__EmptyArg__`.
Be aware that your function will this still receive the argument with the special value and it's up to the user to handle it.


```python
from fancy_signatures import validate, arg


@validate
def empty_arg(a: int, b: int | __EmptyArg__ = arg(required=False)) -> None:
    print(type(a))
    print(type(b))


empty_arg(3)

""""
Output:
<class 'int'>
<class 'fancy_signatures.core.types.__EmptyArg__'>
""""
```


It's also possible to validate related arguments using the `Related` object.


```python
from fancy_signatures import validate, arg
from fancy_signatures.validation import Related


def should_be_greater(a, b):
    if a <= b:
        raise ValueError("a should be greater than b")


@validate(related=[Related(should_be_greater, "a", "b")])
def related(a: int b: int) -> int: 
    return a + b


related(6, 5)  # OK
related(4, 5)  # Raises ValidationError
```

Note that the parameters are named the same in the validation function `should_be_greater` then they are in the main function.
Internally `fancy_signatures` figures out which arguments are required for the validation function and passes them as kwargs to your function


Of course, you can mix and match the functionalities at will.

```python
from fancy_signatures import validate, arg
from fancy_signatures.validation import Related, IntDefault, IntMin


@validate(lazy=True, related=[Related(should_be_greater, "a", "b")])
def my_func(
    a: int = arg(default=IntDefault(0), validators=[IntMin(0)]), 
    b: int = arg(default=IntDefault(1), validators=[IntMin(0)])
) -> int: 
    return a + b
```


Type hints of non-builtins will also work, as long as they are not generics (they inherit from `typing.Generic`) for handling custom generics see the
section on extending the library.

For example, say your parameter is a `pydantic.BaseModel`

```python
from fancy_signatures import validate, arg 

from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int


@validate
def pydantic_func(persons: list[Person], min_age: int = arg(required=True)) -> Person:
    ...
```

Because of the auto-typecasting done by `fancy_signatures` you can pass a `dict` of kwargs and it'll be unpacked for you.

```python
input_dict = {
    "persons": [
        {
            "name": "A",
            "age": "27",
        },
        {
            "name": "B",
            "age": "25",
        },
    ],
    "min_age": "20",
}

pydantic_func(**input_dict)  # OK

# Partial unpacking is also supported

persons_list =  [
    {
        "name": "A",
        "age": "27",
    },
    {
        "name": "B",
        "age": "25",
    },
]

pydantic_func(persons=persons_list, max_age=20)  # Also OK
```


## Extending the package
The package is built with extension support in mind. 


You can provide your own custom validator. Just inherit from the `Validator` base class.


```python
from fancy_signatures import validate, arg
from fancy_signatures.core.interface import Validator
from fancy_signatures.core.exceptions import ValidationError


class ValidateDevisibleByTwo(Validator[int | float]):
    def __call__(self, name: str, obj: int | float) -> int | float:
        if obj % 2 != 0:
            raise ValidationError("Should be divisible by 2", name)
        return obj


@validate
def custom_validator(a: int = arg(validators=[ValidateDevisibleByTwo()])) -> int:
    return a
```


Similarly, you can also provide your own `Default` class. Be aware though that defaults are applied **before** typecasting. Hence,
you are not guaranteed that the type of the value is actually what you'd expect. It's probably wise to use a try..except block


```python
from fancy_signatures import validate, arg
from fancy_signatures.core.interface import Default


class NeverBiggerThanTen(Default[int]):
    def __call__(self, value: Any) -> int:
        if isinstance(value, __EmptyArg__):
            return 0
        elif value > 10:
            return 10
        return value
        

@validate
def custom_default(a: int = arg(default=NeverBiggerThanTen())) -> int:
    return a


custom_default()  # Returns 0
custom_default(8)  # Returns 8
custom_default(22)  # Returns 10
```

As mentioned before, hinting your custom classes should work fine with the only exception of classes that inherit from `typing.Generic`. 
If your class does so, you should add a handler to `GenericAliasTypecaster`.

Support for common generics such as `list`, `dict` and `tuple` are built-in. If your generic is not, it's quite easy to add one.
Say for example you want to support a `numpy.ndarray`.


```python
from typing import get_args
from fancy_signatures import validate, arg
from fancy_signatures.core.interface import TypeCaster
from fancy_signatures.typecasting import GenericAliasTypecaster, typecaster_factory


def handle_np_array(type_hint: type) -> TypeCaster:
    elements_type = get_args(type_hint)[0]
    
    def _handler_func(value: np.array) -> np.array:
        return [typecaster_factory(elements_type)(el) for el in value]
    
    return TypeCaster(_handler_func)


GenericAliasTypecaster.add_handler(np.ndarray, handle_np_array)


@validate
def custom_handler(arr: np.ndarray[str | int | np.int16 | np.int32 | np.int64]) -> np.array:
    return arr
```


Note how `typecaster_factory` is used here once we are back to a type that can be handled by the built-in functionality again.
Internally, each `TypeCaster` casts one origin type hint and calls `typecaster_factory` again for the next hint. This way you will only have
to add minimal code.