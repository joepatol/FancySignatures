from typing import TypeAlias, Any
from .core.interface import TypeCaster


__all__ = ["reset", "set", "get_typecast_handlers"]


class Settings:
    WARN_ON_HANDLER_OVERRIDE: bool = True


class _SettingsTypes:
    WARN_ON_HANDLER_OVERRIDE = bool


def reset() -> None:
    """Reset all settings to their default values"""
    Settings.WARN_ON_HANDLER_OVERRIDE = True


def set(setting: str, value: Any) -> None:
    """Change a setting value

    Args:
        setting (str): The name of the setting (case insensitive)
        value (bool): The new value of the setting

    Raises:
        ValueError: If setting doesn't exist
    """
    _internal_name = setting.upper()

    if not hasattr(Settings, _internal_name):
        raise ValueError(f"Setting {setting} doesn't exist")

    should_be_type = getattr(_SettingsTypes, _internal_name)

    if not isinstance(value, should_be_type):
        raise TypeError(f"Setting '{setting}' should be of type '{should_be_type}'")

    setattr(Settings, _internal_name, value)


def get_typecast_handlers() -> dict[str, dict[TypeAlias, type[TypeCaster]]]:
    """Get all the current registered typecasters a a dictionairy

    Returns:
        dict[str, dict[TypeAlias, type[TypeCaster]]]: Dict containing the stict and non strict handlers
    """
    from .typecasting.__handler_lib import CUSTOM_HANDLERS, STRICT_CUSTOM_HANDLERS

    return {
        "strict_handlers": STRICT_CUSTOM_HANDLERS,
        "handlers": CUSTOM_HANDLERS,
    }
