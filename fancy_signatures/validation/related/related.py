from typing import Any, Callable

from fancy_signatures.exceptions import ValidationError, ValidatorFailed


class Related:
    def __init__(self, func: Callable[..., None], *args: str, **kwargs: str) -> None:
        self._func_args = args
        self._func_kwargs = kwargs
        self._func = func

    def __call__(self, **kwargs: Any) -> Any:
        function_kwargs = {k: v for k, v in kwargs.items() if k in self._func_args}

        for arg in self._func_args:
            if arg not in function_kwargs:
                raise TypeError(
                    f"{self._func.__name__} applies to argument '{arg}' but it wasn't found" "in the function arguments"
                )

        for validation_func_arg_name, kwarg_name in self._func_kwargs.items():
            try:
                value = kwargs[kwarg_name]
            except KeyError:
                raise TypeError(
                    f"{self._func.__name__} applies to argument '{kwarg_name}' but it wasn't found"
                    "in the function arguments"
                )
            function_kwargs[validation_func_arg_name] = value
        try:
            self._func(**function_kwargs)
        except ValidatorFailed as e:
            raise ValidationError(str(e), list(self._func_args) + list(self._func_kwargs.values()))
