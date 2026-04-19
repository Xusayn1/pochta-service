"""
Dynamic settings loader.

Allows using ``DJANGO_SETTINGS_MODULE=core.settings`` while the actual
environment-specific module is picked from ``core.config`` (defaulting
to ``core.settings.dev`` or whatever is set in .env).
"""

import os
from importlib import import_module

from core import config

# Prefer the module from .env, but if someone set DJANGO_SETTINGS_MODULE to
# "core.settings", fall back to development settings by default.
_default_target = (
    config.DJANGO_SETTINGS_MODULE
    if config.DJANGO_SETTINGS_MODULE not in ("core.settings", "", None)
    else "core.settings.dev"
)

_target = os.environ.get("DJANGO_SETTINGS_MODULE") or _default_target
if _target in ("core.settings", __name__, "", None):
    _target = _default_target

# Import the concrete settings module and copy its uppercase attributes
_module = import_module(_target)

for _attr in dir(_module):
    if _attr.isupper():
        globals()[_attr] = getattr(_module, _attr)

# Keep things tidy
__all__ = [name for name in globals() if name.isupper()]
