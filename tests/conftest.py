from typing import Any, Generator
import pytest

from fancy_signatures.settings import reset as settings_reset
from fancy_signatures.core.interface import TypeCaster
from fancy_signatures.exceptions import TypeCastError
from fancy_signatures.typecasting import register_handler, unregister_strict_handler


class IntTypeCaster(TypeCaster[int]):
    def validate(self, param_value: Any) -> bool:
        return isinstance(param_value, int)

    def cast(self, param_value: Any) -> int:
        if isinstance(param_value, str):
            try:
                param_value = eval(param_value)
            except Exception:
                raise TypeCastError(int)
        if isinstance(param_value, float):
            raise TypeCastError(int)
        try:
            return int(param_value)
        except TypeError:
            raise TypeCastError(int)


@pytest.fixture(scope="function")
def custom_int_handler() -> Generator[bool, None, None]:
    register_handler(type_hints=[int], handler=IntTypeCaster, strict=True)
    yield True
    unregister_strict_handler(int)


@pytest.fixture(scope="function")
def reset_settings() -> Generator[bool, None, None]:
    yield True
    settings_reset()
