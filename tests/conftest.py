from typing import Any, Generator
import pytest

from fancy_signatures.settings import reset as settings_reset, set, ProtocolHandlingLevel
from fancy_signatures.core.interface import TypeCaster
from fancy_signatures.exceptions import TypeCastError
from fancy_signatures.typecasting import register_typecaster, unregister_strict_typecaster


class ExceptionNotRaised(Exception):
    def __init__(self) -> None:
        super().__init__(
            "This test expected an error to be raised and test the resulting error."
            "However, the error was not raised at all."
        )


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
    set("WARN_ON_HANDLER_OVERRIDE", False)
    register_typecaster(type_hints=[int], handler=IntTypeCaster, strict=True)
    yield True
    unregister_strict_typecaster(int)
    settings_reset()


@pytest.fixture(scope="function")
def reset_settings() -> Generator[bool, None, None]:
    yield True
    settings_reset()


@pytest.fixture(scope="function")
def protocol_warnings_enabled() -> Generator[bool, None, None]:
    set("PROTOCOL_HANDLING", ProtocolHandlingLevel.WARN)
    yield True
    settings_reset()


@pytest.fixture(scope="function")
def disallow_protocols() -> Generator[bool, None, None]:
    set("PROTOCOL_HANDLING", ProtocolHandlingLevel.DISALLOW)
    yield True
    settings_reset()
