from typing import Any, Callable

from ..core.exceptions import ValidationError


class Related:
    def __init__(self, func: Callable, *params: str) -> None:
        self._params = params
        self._func = func
        
    def __call__(self, **kwargs: Any) -> Any:
        function_kwargs = {k: v for k, v in kwargs.items() if k in self._params}
        try:
            self._func(**function_kwargs)
        except Exception as e:
            raise ValidationError(e, str(self._params))
