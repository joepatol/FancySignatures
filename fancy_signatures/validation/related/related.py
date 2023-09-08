from typing import Any, Callable

from fancy_signatures.exceptions import ValidationError, ValidatorFailed


class Related:
    def __init__(self, func: Callable[..., None], *args: str, **kwargs: str) -> None:
        self._func_args = args
        self._func_kwargs = kwargs
        self._func = func

    def __call__(self, **kwargs: Any) -> Any:
        function_kwargs = {k: v for k, v in kwargs.items() if k in self._func_args}
        for validation_func_arg_name, kwarg_name in self._func_kwargs.items():
            function_kwargs[validation_func_arg_name] = kwargs[kwarg_name]
        try:
            self._func(**function_kwargs)
        except ValidatorFailed as e:
            raise ValidationError(str(e), list(self._func_args) + list(self._func_kwargs.values()))
