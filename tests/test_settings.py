import pytest
from typing import Any
from contextlib import nullcontext as does_not_raise

from fancy_signatures.settings import set, get_typecast_handlers, Settings, ProtocolHandlingLevel
from fancy_signatures.typecasting import register_typecaster
from fancy_signatures.typecasting.default import DefaultTypeCaster
from fancy_signatures.typecasting.special_origins import StringTypeCaster


def test__setting_default() -> None:
    assert Settings.WARN_ON_HANDLER_OVERRIDE is True
    assert Settings.PROTOCOL_HANDLING == ProtocolHandlingLevel.ALLOW
    assert Settings.ALLOW_TUPLE_ADDITIONAL_PARAMS is True


def test__change_setting(reset_settings: bool) -> None:
    assert reset_settings is True
    set("WARN_ON_HANDLER_OVERRIDE", False)
    assert Settings.WARN_ON_HANDLER_OVERRIDE is False


def test_default_handlers() -> None:
    handlers_dict = get_typecast_handlers()
    assert len(handlers_dict["strict_handlers"]) == 12
    assert len(handlers_dict["handlers"]) == 3


def test__warning_raised_when_handler_override(reset_settings: bool) -> None:
    assert reset_settings is True

    with pytest.warns(UserWarning):
        register_typecaster(type_hints=[str], handler=DefaultTypeCaster, strict=True)

    set("WARN_ON_HANDLER_OVERRIDE", False)

    with does_not_raise():
        register_typecaster(type_hints=[str], handler=StringTypeCaster, strict=True)


@pytest.mark.parametrize(
    "setting_name, value",
    [
        ("WARN_ON_HANDLER_OVERRIDE", "true"),
        ("PROTOCOL_HANDLING", "ALLOW"),
    ],
)
def test__settings_invalid_type(setting_name: str, value: Any) -> None:
    with pytest.raises(TypeError):
        set(setting_name, value)
