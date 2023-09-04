from typing import Any, Callable

from ..core.exceptions import ValidationError


class Related:
    def __init__(self, func: Callable, *args: str, **kwargs: str) -> None:
        self._func_args = args
        self._func_kwargs = kwargs
        self._func = func

    def __call__(self, **kwargs: Any) -> Any:
        function_kwargs = {k: v for k, v in kwargs.items() if k in self._func_args}
        for validation_func_arg_name, kwarg_name in self._func_kwargs.items():
            function_kwargs[validation_func_arg_name] = kwargs[kwarg_name]
        try:
            self._func(**function_kwargs)
        except Exception as e:
            raise ValidationError(str(e), str(list(self._func_args) + list(self._func_kwargs.values())))
