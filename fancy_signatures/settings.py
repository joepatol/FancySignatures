from typing import TypeAlias
from .core.interface import TypeCaster


class Settings:
    WARN_ON_HANDLER_OVERRIDE = True


def set(setting: str, value: bool) -> None:
    if not hasattr(Settings, setting.upper()):
        raise ValueError(f"Setting {setting} doesn't exist")

    setattr(Settings, setting.upper(), value)


def get_typecast_handlers() -> dict[str, dict[TypeAlias, type[TypeCaster]]]:
    from .typecasting.handlers import _CUSTOM_HANDLERS, _STRICT_CUSTOM_HANDLERS

    return {
        "strict_handlers": _STRICT_CUSTOM_HANDLERS,
        "handlers": _CUSTOM_HANDLERS,
    }
