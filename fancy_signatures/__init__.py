"""
.. include:: ../README.md
"""

from .api import argument, validate  # noqa
from .core.interface import TypeCaster, Validator, Default  # noqa
from .core.empty import is_empty  # noqa
from .typecasting.handlers import register_typecaster, unregister_typecaster, unregister_strict_typecaster  # noqa
from .settings import set as adjust_setting, reset as reset_settings  # noqa
from .__version__ import __version__  # noqa
