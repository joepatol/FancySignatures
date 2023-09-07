from typing import TypeAlias
from .core.interface import TypeCaster


class Settings:
    WARN_ON_HANDLER_OVERRIDE = True


def reset() -> None:
    """Reset all settings to their default values"""
    Settings.WARN_ON_HANDLER_OVERRIDE = True


def set(setting: str, value: bool) -> None:
    """Change a setting value

    Args:
        setting (str): The name of the setting (case insensitive)
        value (bool): The new value of the setting

    Raises:
        ValueError: If setting doesn't exist
    """
    if not hasattr(Settings, setting.upper()):
        raise ValueError(f"Setting {setting} doesn't exist")

    setattr(Settings, setting.upper(), value)


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
