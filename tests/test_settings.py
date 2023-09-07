import pytest

from fancy_signatures.settings import set, get_typecast_handlers, Settings
from fancy_signatures.typecasting import register_handler
from fancy_signatures.typecasting.default import DefaultTypeCaster


def test__setting_default() -> None:
    assert Settings.WARN_ON_HANDLER_OVERRIDE is True


def test__change_setting(reset_settings: bool) -> None:
    assert reset_settings is True
    set("WARN_ON_HANDLER_OVERRIDE", False)
    assert Settings.WARN_ON_HANDLER_OVERRIDE is False


def test_default_handlers() -> None:
    handlers_dict = get_typecast_handlers()
    assert len(handlers_dict["strict_handlers"]) == 6
    assert len(handlers_dict["handlers"]) == 4


def test__warning_raised() -> None:
    with pytest.raises(UserWarning):
        register_handler(type_hints=[list], handler=DefaultTypeCaster, strict=False)
